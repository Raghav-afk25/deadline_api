import os
from dotenv import load_dotenv

load_dotenv()

# Telegram + Database
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
SONG_DB_CHANNEL = int(os.getenv("SONG_DB_CHANNEL", "0"))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "deadline_api")

# Proxy
PROXY_HOST = os.getenv("PROXY_HOST", "")
PROXY_PORT = int(os.getenv("PROXY_PORT", "0"))
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")
PROXY = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}" if PROXY_HOST else None

# Cookies
COOKIES_PATH = os.getenv("COOKIES_PATH", os.path.join(os.getcwd(), "cookies", "cookies.txt"))

# Plans (req/minute)
PLANS = {
    "FREE": 5,
    "BASIC": 20,
    "PRO": 60,
}

# API KEYS mapping → PLAN
API_KEYS = {
    "FRJAXEVZ0CBC": "FREE",
    "ABCD1234PLANBASIC": "BASIC",
    "XYZ9876PLANPRO": "PRO",
}
