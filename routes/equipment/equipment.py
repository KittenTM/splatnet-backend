from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session as UserSession, Equipment, EquipmentLast
from services import auth
from config import cipher
import json
import os

router = APIRouter()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GEAR_SKILLS_PATH = os.path.join(CURRENT_DIR, "abilitymain.json")
with open(GEAR_SKILLS_PATH, "r") as f:
    GEAR_SKILLS = json.load(f)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/equipment")
async def get_equipment_composite(request: Request, db: DBSession = Depends(get_db)):
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
        mii_name = profile.get("name", user.username)
        
        last_gear = db.query(EquipmentLast).filter(EquipmentLast.PId == pid_val).first()

        if last_gear:
            data = {column.name: getattr(last_gear, column.name) for column in last_gear.__table__.columns}
            
            hed_id = str(data.get("Gear_Head", "0"))
            clt_id = str(data.get("Gear_Clothes", "0"))
            shs_id = str(data.get("Gear_Shoes", "0"))

            gear_data = {
                "PId": data.get("PId"),
                "Rank": data.get("Rank"),
                "Udemae": data.get("Udemae"),
                "weapon": data.get("weapon"),
                "Gear_Head": data.get("Gear_Head"),
                "Gear_Clothes": data.get("Gear_Clothes"),
                "Gear_Shoes": data.get("Gear_Shoes"),
                
                # have to do this tomfoolery because ninty was a dumbass.
                # discovered this only AFTER making most of the code that
                # the /post doesnt actually send ur main ability. So its undetectable!!
                # Yay!!!! also means gotta code in our own main ability
                "Gear_Head_Skill0": GEAR_SKILLS.get("HeadGear", {}).get(hed_id, {}).get("Skill0"),
                "Gear_Head_Skill1": data.get("Gear_Head_Skill0"),
                "Gear_Head_Skill2": data.get("Gear_Head_Skill1"),
                "Gear_Head_Skill3": data.get("Gear_Head_Skill2"),

                  "Gear_Clothes_Skill0": GEAR_SKILLS.get("Clothes", {}).get(clt_id, {}).get("Skill0"),
                "Gear_Clothes_Skill1": data.get("Gear_Clothes_Skill0"),
                "Gear_Clothes_Skill2": data.get("Gear_Clothes_Skill1"),
                "Gear_Clothes_Skill3": data.get("Gear_Clothes_Skill2"),

                "Gear_Shoes_Skill0": GEAR_SKILLS.get("Shoes", {}).get(shs_id, {}).get("Skill0"),
                "Gear_Shoes_Skill1": data.get("Gear_Shoes_Skill0"),
                "Gear_Shoes_Skill2": data.get("Gear_Shoes_Skill1"),
                "Gear_Shoes_Skill3": data.get("Gear_Shoes_Skill2"),
            }
        else:
            gear_data = None

        return {
            "mii_name": mii_name,
            "last_equipped": gear_data
        }
    except Exception as e:
        print(f"Equipment Route Error: {e}")
        return {"mii_name": user.username, "last_equipped": None}