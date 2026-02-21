from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session as UserSession
from services import auth
from config import cipher

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me")
async def get_my_profile(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="No active session")

    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = db.query(User).filter(User.username == db_session.username).first()
    if not user or not user.spfn_pass_enc:
        raise HTTPException(status_code=401, detail="Credentials not found. Please re-login.")

    try:
        decrypted_pass = cipher.decrypt(user.spfn_pass_enc.encode()).decode()

        token_data = auth.get_token(user.username, decrypted_pass)
        if not token_data or "token" not in token_data:
            raise HTTPException(status_code=401, detail="External authentication failed")

        profile_data = auth.get_profile(token_data["token"])
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return profile_data

    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")