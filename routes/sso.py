from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import RedirectResponse
from typing import Optional
from services import auth

router = APIRouter()

@router.post('/spfn/generate_token')
async def login(
    request: Request, 
    username: Optional[str] = Form(None), 
    password: Optional[str] = Form(None),
    frontend_origin: Optional[str] = Form(None)
):
    host = (frontend_origin or request.headers.get("referer") or "/").rstrip('/')
    sep = "&" if "?" in host else "?"

    if not username or not password:
        return RedirectResponse(f"{host}/users/auth/splatfestival/{sep}error=auth&username={username or ''}", 303)

    try:
        token = auth.get_token(username, password)
        if not token:
            return RedirectResponse(f"{host}/users/auth/splatfestival/{sep}error=auth&username={username}", 303)

        # Logging profile for debugging
        profile = auth.get_profile(token)
        if profile:
            print(f"=== PROFILE ===\n{profile}\n===============")

        redirect_arg = request.query_params.get('redirect')
        target = redirect_arg if redirect_arg else f"{host}/friend_list/"
        return RedirectResponse(url=target, status_code=303)

    except Exception as e:
        return Response(content=f"Proxy Error: {str(e)}", status_code=500)