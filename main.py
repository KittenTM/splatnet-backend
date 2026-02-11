from fastapi import FastAPI, Request
from routes import sso, user
from config import settings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

@app.middleware("http")
async def force_cors_on_errors(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin == settings.frontend_url:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

app.include_router(sso.router, prefix="/api/v2/sso")
app.include_router(user.router, prefix="/api/v1/users")

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
    init_db()