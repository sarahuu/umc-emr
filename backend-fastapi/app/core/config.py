from pydantic_settings import BaseSettings
import os

from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Odoo Auth Wrapper"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ODOO_URL: str = os.getenv("ODOO_URL")
    ODOO_DB: str = os.getenv("ODOO_DB")
    ODOO_API_KEY: str = os.getenv('ODOO_API_KEY')
    REDIS_URL: str = os.getenv('REDIS_URL')
    ENCRYPTION_KEY:str = os.getenv("ENCRYPTION_KEY")

settings = Settings()
