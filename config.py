from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    port: int = 5000
    db_url: str
    fernet_key: str
    cookie_httponly: bool = True
    frontend_url: str
    boss_url: str
    boss_aes_key: str
    boss_hmac_key: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    cookie_secure: bool = True

settings = Settings()
cipher = Fernet(settings.fernet_key.encode())