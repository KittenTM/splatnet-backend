import requests
from config import settings
from argon2 import PasswordHasher

API_URL = "https://account.spfn.net/api/v2"
CLIENT_ID = "splatnet"
CLIENT_SECRET = settings.account_client_secret
ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password)

def get_token(username, password):
    url = f"{API_URL}/oauth2/generate_token"
    
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    headers = {
        "User-Agent": "chiyo & eri should lwk kiss..."
    }
    
    response = requests.post(url, data=payload, headers=headers, timeout=10)
    return response.json() if response.ok else None

def get_profile(token):
    url = f"{API_URL}/users/@me/profile"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "lets make the most of the night like were gonna die young!!"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    return response.json() if response.ok else None