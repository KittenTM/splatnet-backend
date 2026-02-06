from fastapi import FastAPI
from routes import sso
from database import init_db
from config import settings
import uvicorn

app = FastAPI()

init_db()

app.include_router(sso.router, prefix="/api/v2/sso")

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)