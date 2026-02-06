from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from routes import sso
import uvicorn

class Settings(BaseSettings):
    port: int = 5000
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

app = FastAPI()
app.include_router(sso.router, prefix="/api/v2/sso")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=settings.port)