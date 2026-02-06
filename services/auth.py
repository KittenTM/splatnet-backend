import requests
import base64
from argon2 import PasswordHasher

API_URL = "https://account.spfn.net/api/v2"
ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password)

def verify_password(hashed: str, password: str):
    try:
        return ph.verify(hashed, password)
    except Exception:
        return False

def get_token(username, password):
    creds = f"{username} {password}"
    encoded = base64.b64encode(creds.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded}",
        "User-Agent": "saturday & allison should lwk kiss..."
    }
    
    response = requests.get(f"{API_URL}/oauth2/generate_token", headers=headers, timeout=10)
    return response.json() if response.ok else None

def get_profile(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "every update im going to change this user agent because im bored!!"
    }
    response = requests.get(f"{API_URL}/users/@me/profile", headers=headers, timeout=10)
    return response.text if response.ok else None