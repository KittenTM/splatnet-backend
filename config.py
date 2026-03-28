from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    port: int = 5000
    judd_port: int = 4000
    db_url: str
    fernet_key: str
    cookie_httponly: bool = True
    frontend_url: str
    boss_url: str
    boss_aes_key: str
    boss_hmac_key: str
    twitter_client_id: str
    twitter_client_secret: str
    twitter_redirect_uri: str

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.getcwd(), ".env"), 
            #fallback
            BASE_DIR / ".env"
        ],
        env_file_encoding='utf-8',
        extra="ignore"
    )
    cookie_secure: bool = True
    webhook_url: str

settings = Settings()
cipher = Fernet(settings.fernet_key.encode())