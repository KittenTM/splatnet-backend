import requests
import base64

API_URL = "https://account.spfn.net/api/v2"

def get_token(username, password):
    creds = f"{username} {password}"
    encoded = base64.b64encode(creds.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded}",
        "User-Agent": "saturday & allison should lwk kiss..."
    }
    
    response = requests.get(f"{API_URL}/oauth2/generate_token", headers=headers, timeout=10)
    return response.json().get("token") if response.ok else None

def get_profile(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "every update im going to change this user agent because im bored!!"
    }
    response = requests.get(f"{API_URL}/users/@me/profile", headers=headers, timeout=10)
    return response.text if response.ok else None