import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "captcha_db")

# Application Configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

CAPTCHA_SIZE = int(os.getenv("CAPTCHA_SIZE", 1000))
CAPTCHA_GRID_SIZE = int(os.getenv("CAPTCHA_GRID_SIZE", 700))
CAPTCHA_OUTPUT_DIR = os.getenv("CAPTCHA_OUTPUT_DIR", "captchas")
CAPTCHA_IMAGE_PATH = os.getenv("CAPTCHA_IMAGE_PATH", "octopus.png")

SYSTEM_STATS_INTERVAL = int(os.getenv("SYSTEM_STATS_INTERVAL", 5))  # seconds
HISTORY_RETENTION_DAYS = int(os.getenv("HISTORY_RETENTION_DAYS", 1))

os.makedirs(CAPTCHA_OUTPUT_DIR, exist_ok=True)

COLLECTIONS = {
    "captcha_stats": "captcha_stats",
    "system_stats": "system_stats",
}
