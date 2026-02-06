from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, Response
import requests
import base64
from typing import Optional

app = FastAPI()

SPFN_API_URL = "https://account.spfn.net/api/v2/oauth2/generate_token"

def generate_spfn_token(encoded_creds):
    headers = {
        "Authorization": f"Basic {encoded_creds}",
        "User-Agent": "saturday & allison should lwk kiss..."
    }
    response = requests.get(SPFN_API_URL, headers=headers, timeout=10)
    return response.json().get("token") if response.ok else None

@app.post('/api/v2/sso/spfn/generate_token')
async def handle_login(
    request: Request, 
    username: Optional[str] = Form(None), 
    password: Optional[str] = Form(None),
    # added optional so everything doesnt crash and burn if it doesnt exist... it probably still will though.
    frontend_origin: Optional[str] = Form(None)
):
    login_host = frontend_origin or request.headers.get("referer") or "/"
    
    if login_host.endswith('/'):
        login_host = login_host[:-1]

    if not username or not password:
        sep = "&" if "?" in login_host else "?"
        error_url = f"{login_host}/users/auth/splatfestival/{sep}error=auth&username={username or ''}"
        return RedirectResponse(url=error_url, status_code=303)

    creds = f"{username} {password}"
    encoded_creds = base64.b64encode(creds.encode()).decode()

    try:
        token = generate_spfn_token(encoded_creds)

        #if onika eats burgers then does oomi appear?
        if token:
            print("=== TOKEN ===", token, "===========", sep="\n")

            profile_headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "every update im going to change this user agent because im bored!!"
            }

            profile_response = requests.get(
                "https://account.spfn.net/api/v2/users/@me/profile",
                headers=profile_headers,
                timeout=10
            )

            if profile_response.ok:
                print("=== PROFILE ===", profile_response.text, "===============", sep="\n")
            redirect_arg = request.query_params.get('redirect')
            redirect_to = redirect_arg if redirect_arg else f"{login_host}/friend_list/"
            return RedirectResponse(url=redirect_to, status_code=303)
        else:
            sep = "&" if "?" in login_host else "?"
            error_url = f"{login_host}/users/auth/splatfestival/{sep}error=auth&username={username}"
            return RedirectResponse(url=error_url, status_code=303)

    except Exception as e:
        return Response(content=f"Proxy Error: {str(e)}", status_code=500)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)