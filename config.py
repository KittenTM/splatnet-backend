from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    port: int = 5000
    db_url: str
    fernet_key: str
    cookie_httponly: bool = False
    frontend_url: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    cookie_secure: bool = False

settings = Settings()
cipher = Fernet(settings.fernet_key.encode())