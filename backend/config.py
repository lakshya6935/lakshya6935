import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/hotel_management")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = 24
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@stayluxe.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@12345")
    PORT = int(os.getenv("PORT", 5000))
