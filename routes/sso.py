from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session
from config import settings, cipher
from services import auth
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/spfn/generate_token')
async def login(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...),
    frontend_origin: str = Form(None),
    rememberMe: bool = Form(False),
    db: DBSession = Depends(get_db)
):
    host = (frontend_origin or request.headers.get("referer") or "/").rstrip('/')
    
    try:
        print("fetching spfn token")
        data = auth.get_token(username, password)
        if not data or "token" not in data:
            print("auth failed")
            return RedirectResponse(f"{host}/login?error=auth", 303)

        print("encrypting password")
        enc_pass = cipher.encrypt(password.encode()).decode()
        
        print(f"checking user {username}")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print("creating new user")
            user = User(
                username=username, 
                local_hash=auth.hash_password(password), 
                spfn_pass_enc=enc_pass
            )
            db.add(user)
        else:
            print("updating user")
            user.spfn_pass_enc = enc_pass
        
        db.flush() 
        
        print("creating session")
        new_session = Session(username=username, remember_me=rememberMe)
        db.add(new_session)
        db.commit()

        print("setting cookie and redirecting")
        response = RedirectResponse(url=f"{host}/friend_list/", status_code=303)
        cookie_age = 2592000 if rememberMe else None
        
        response.set_cookie(
            key="session_id",
            value=new_session.id,
            httponly=settings.cookie_httponly,
            secure=True,
            samesite="lax",
            max_age=cookie_age
        )
        return response

    except Exception as e:
        print(f"error: {str(e)}")
        db.rollback()
        return Response(content=f"internal error: {str(e)}", status_code=500)