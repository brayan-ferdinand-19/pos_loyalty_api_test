import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "POS Orders & Customer Loyalty API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/pos_loyalty"
    )
    TIMEZONE: str = "Asia/Colombo"

settings = Settings()
