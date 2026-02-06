from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session
from config import settings, cipher
from services import auth
from typing import Optional
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
    username: Optional[str] = Form(None), 
    password: Optional[str] = Form(None),
    frontend_origin: Optional[str] = Form(None),
    rememberMe: bool = Form(False),
    db: DBSession = Depends(get_db)
):
    host = (frontend_origin or request.headers.get("referer") or "/").rstrip('/')
    sep = "&" if "?" in host else "?"
    auth_path = f"{host}/users/auth/splatfestival/"
    print(f"host: {host}")

    if not username or not password:
        print("blank fields detected")
        return RedirectResponse(f"{auth_path}{sep}error=auth&username={username or ''}", 303)

    try:
        print("fetching spfn token")
        data = auth.get_token(username, password)
        if not data or "token" not in data:
            print("auth failed")
            return RedirectResponse(f"{auth_path}{sep}error=auth&username={username}", 303)

        print(f"checking user {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print("creating new user with argon2id")
            enc_pass = cipher.encrypt(password.encode()).decode() if rememberMe else ""
            user = User(
                username=username, 
                local_hash=auth.hash_password(password), 
                spfn_pass_enc=enc_pass
            )
            db.add(user)
        elif rememberMe:
            print("updating encrypted pass for client")
            user.spfn_pass_enc = cipher.encrypt(password.encode()).decode()
        else:
            print("client requested no password storage, skipping update")
        
        db.flush() 

        print("checking for existing session")
        active_session = db.query(Session).filter(Session.username == username).first()
        
        if active_session:
            print(f"refreshing session for {username}")
            active_session.remember_me = rememberMe
        else:
            print(f"creating new session for {username}")
            active_session = Session(username=username, remember_me=rememberMe)
            db.add(active_session)

        db.commit()

        print("setting client-based cookie")
        response = RedirectResponse(url=f"{host}/friend_list/", status_code=303)
        cookie_age = 2592000 if rememberMe else None
        
        #you are a pain in the ass respectfully
        response.set_cookie(
            key="session_id",
            value=active_session.id,
            httponly=settings.cookie_httponly,
            secure=False,
            samesite="lax",
            path="/",
            max_age=cookie_age,
            domain=None
        )
        return response

    except Exception as e:
        print(f"error: {str(e)}")
        db.rollback()
        return Response(content=f"internal error: {str(e)}", status_code=500)