from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import SessionLocal, User, Session as UserSession, TwitterLink 
from config import settings, cipher
from services import auth
import secrets
import hashlib
import base64
import httpx 
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pkce_store = {}

@router.get("/me/twitter/link")
async def link_twitter(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=401)

    state = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64)
    
    sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').replace('=', '')

    pkce_store[state] = {
        "verifier": verifier,
        "username": db_session.username
    }

    scopes = "tweet.read tweet.write users.read offline.access"
    encoded_scopes = scopes.replace(" ", "%20")
    
    base_url = "https://twitter.com/i/oauth2/authorize"
    params = [
        "response_type=code",
        f"client_id={settings.twitter_client_id}",
        f"redirect_uri={settings.twitter_redirect_uri}",
        f"scope={encoded_scopes}",
        f"state={state}",
        f"code_challenge={challenge}",
        "code_challenge_method=S256"
    ]
    
    return {"url": f"{base_url}?{'&'.join(params)}"}

@router.get("/me/twitter/confirm")
async def confirm_twitter(state: str, code: str, db: DBSession = Depends(get_db)):
    stored_data = pkce_store.get(state)
    if not stored_data:
        raise HTTPException(status_code=400, detail="State not found.")

    auth_str = f"{settings.twitter_client_id}:{settings.twitter_client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            headers={"Authorization": f"Basic {encoded_auth}", "Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.twitter_redirect_uri,
                "code_verifier": stored_data["verifier"],
            }
        )

    token_data = token_res.json()
    if token_res.status_code != 200:
        raise HTTPException(status_code=401, detail="Twitter auth failed")

    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
    handle = user_res.json().get("data", {}).get("username")

    user = db.query(User).filter(User.username == stored_data["username"]).first()
    if not user or not user.spfn_pass_enc:
        raise HTTPException(status_code=404, detail="Local user not found")

    decrypted_pass = cipher.decrypt(user.spfn_pass_enc.encode()).decode()
    profile_auth = auth.get_token(user.username, decrypted_pass)
    
    profile_response = auth.get_profile(profile_auth["token"])
    
    if isinstance(profile_response, str):
        try:
            profile_data = json.loads(profile_response)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse player profile JSON")
    else:
        profile_data = profile_response

    if not profile_data:
        raise HTTPException(status_code=500, detail="Could not fetch player profile")

    pid = profile_data.get("pid")
    mii_data = profile_data.get("mii", {}).get("data")

    def encrypt_val(val: str):
        return cipher.encrypt(val.encode()).decode() if val else None

    tw_link = db.query(TwitterLink).filter(TwitterLink.pid == pid).first()
    if not tw_link:
        tw_link = TwitterLink(pid=pid)
        db.add(tw_link)

    tw_link.twitter_handle = handle
    tw_link.twitter_token_enc = encrypt_val(token_data["access_token"])
    tw_link.twitter_refresh_token_enc = encrypt_val(token_data.get("refresh_token"))
    tw_link.miidata_enc = encrypt_val(mii_data)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    pkce_store.pop(state, None)

    return {"status": "success", "pid": pid, "handle": handle}

@router.get("/me/twitter/status")
async def get_twitter_status(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.username == db_session.username).first()
    if not user or not user.spfn_pass_enc:
        raise HTTPException(status_code=404)

    try:
        decrypted_pass = cipher.decrypt(user.spfn_pass_enc.encode()).decode()
        profile_auth = auth.get_token(user.username, decrypted_pass)
        profile_res = auth.get_profile(profile_auth["token"])
        
        if isinstance(profile_res, str):
            profile_data = json.loads(profile_res)
        else:
            profile_data = profile_res
            
        pid = profile_data.get("pid")
        
        tw_link = db.query(TwitterLink).filter(TwitterLink.pid == pid).first()
        
        if tw_link:
            return {
                "is_linked": True,
                "twitter_handle": tw_link.twitter_handle
            }
        return {"is_linked": False}

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to check twitter status")

@router.post("/me/twitter/unlink")
async def unlink_twitter(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.username == db_session.username).first()
    decrypted_pass = cipher.decrypt(user.spfn_pass_enc.encode()).decode()
    profile_auth = auth.get_token(user.username, decrypted_pass)
    profile_data = auth.get_profile(profile_auth["token"])
    
    if isinstance(profile_data, str):
        profile_data = json.loads(profile_data)

    pid = profile_data.get("pid")

    tw_link = db.query(TwitterLink).filter(TwitterLink.pid == pid).first()

    if tw_link:
        def decrypt_val(val):
            return cipher.decrypt(val.encode()).decode() if val else None

        access_token = decrypt_val(tw_link.twitter_token_enc)
        refresh_token = decrypt_val(tw_link.twitter_refresh_token_enc)

        auth_str = f"{settings.twitter_client_id}:{settings.twitter_client_secret}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()

        async with httpx.AsyncClient() as client:
            if access_token:
                await client.post(
                    "https://api.twitter.com/2/oauth2/revoke",
                    headers={
                        "Authorization": f"Basic {encoded_auth}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "token": access_token,
                        "token_type_hint": "access_token",
                    },
                )

            if refresh_token:
                await client.post(
                    "https://api.twitter.com/2/oauth2/revoke",
                    headers={
                        "Authorization": f"Basic {encoded_auth}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "token": refresh_token,
                        "token_type_hint": "refresh_token",
                    },
                )

        db.delete(tw_link)
        db.commit()

    return {"status": "success"}