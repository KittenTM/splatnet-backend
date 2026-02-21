from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session
from typing import Dict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/session_id/check')
async def get_current_user(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="No session cookie")
    active_session = db.query(Session).filter(Session.id == session_id).first()
    if not active_session:
        print(f"invalid or expired session: {session_id}")
        raise HTTPException(status_code=401, detail="invalid session")
    user = db.query(User).filter(User.username == active_session.username).first()
    
    if not user:
        print(f"session linked to non-existent user: {active_session.username}")
        raise HTTPException(status_code=401, detail="user not found")
    print(f"auto-login success for {user.username}")
    return {
        "status": "ok",
        "username": user.username
    }