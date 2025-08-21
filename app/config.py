# app/config.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("DB_NAME", "deadline")

API_KEY   = os.getenv("API_KEY", "supersecret")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0") or 0)
OWNER_ID   = int(os.getenv("OWNER_ID", "0") or 0)

COOKIES_PATH = os.getenv("COOKIES_PATH", "cookies/cookies.txt")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

# ── Proxy settings (env > defaults you gave) ──────────────────────────────────
PROXY_HOST = os.getenv("PROXY_HOST", "p.webshare.io")
PROXY_PORT = os.getenv("PROXY_PORT", "80")
PROXY_USER = os.getenv("PROXY_USER", "zclarjnk-rotate")
PROXY_PASS = os.getenv("PROXY_PASS", "83fjqnfinvpm")
PROXY_URL  = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# expose standard envs too so libs respect them
os.environ.setdefault("HTTP_PROXY", PROXY_URL)
os.environ.setdefault("HTTPS_PROXY", PROXY_URL)

# ── Mongo ─────────────────────────────────────────────────────────────────────
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_col = db["users"]
cache_col = db["cache"]
