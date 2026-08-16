import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'fashion_recommendation.db')}"

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_PATH)
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    ALPHA_WEIGHT = float(os.getenv("ALPHA_WEIGHT", 0.5))

settings = Settings()