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

@router.post('/spfn/logout')
async def logout(
    request: Request,
    frontend_origin: Optional[str] = Form(None),
    db: DBSession = Depends(get_db)
):
    host = (frontend_origin or request.headers.get("referer") or "/").rstrip('/')
    redirect_url = f"{host}/sign_in/"
    
    response = RedirectResponse(url=redirect_url, status_code=303)
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
            db.query(Session).filter(Session.id == session_id).delete()
            db.commit()
            print(f"Session {session_id} deleted from database.")
        except Exception as e:
            print(f"Error deleting session: {e}")
            db.rollback()

    response.delete_cookie(
        key="session_id",
        path="/",
        domain=None,
        httponly=settings.cookie_httponly,
        samesite="lax"
    )

    return response