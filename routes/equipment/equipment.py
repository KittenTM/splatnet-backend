from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session as UserSession, Equipment
from services import auth
from config import cipher
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/equipment/history")
async def get_history(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    
    if not db_session:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.username == db_session.username).first()
    
    try:
        decrypted_pass = cipher.decrypt(user.spfn_pass_enc.encode()).decode()
        token_data = auth.get_token(user.username, decrypted_pass)
        profile = json.loads(auth.get_profile(token_data["token"]))
        pid_val = int(profile.get("pid"))
        print(f"Fetching History for PID: {pid_val}")
        
        results = db.query(Equipment).filter(Equipment.PId == pid_val).all()
        return results
    except Exception as e:
        print(f"Error in history route: {e}")
        return []