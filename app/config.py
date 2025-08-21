# app/config.py
import os
from pymongo import MongoClient

# ── Direct config (no .env needed) ────────────────────────────────────────────
MONGO_URI   = "mongodb+srv://smaug571:ZENeRk1gAJhkmaXc@cluster0.ebgdwyo.mongodb.net/?retryWrites=true&w=majority"
DB_NAME     = "cluster0"
API_KEY     = "supersecret"

BOT_TOKEN   = "7638651872:AAHN3nTAeNNFh9pcG5UP2dXXMM_FUjEmC1s"
CHANNEL_ID  = -1002530157716
OWNER_ID    = 8162844043

COOKIES_PATH = "cookies/cookies.txt"
DOWNLOAD_DIR = "downloads"

# ── Proxy settings ────────────────────────────────────────────────────────────
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"
PROXY_USER = "zclarjnk-rotate"
PROXY_PASS = "83fjqnfinvpm"

PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# Expose proxy globally
os.environ.setdefault("HTTP_PROXY", PROXY_URL)
os.environ.setdefault("HTTPS_PROXY", PROXY_URL)

# ── Mongo setup ───────────────────────────────────────────────────────────────
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_col = db["users"]
cache_col = db["cache"]

# ── Plans (daily / monthly limits) ────────────────────────────────────────────
PLANS = {
    "d1k":    {"daily": 1_000,   "monthly": 30_000,    "price_rs": 55},
    "d5k":    {"daily": 5_000,   "monthly": 150_000,   "price_rs": 125},
    "d10k":   {"daily": 10_000,  "monthly": 300_000,   "price_rs": 215},
    "d20k":   {"daily": 20_000,  "monthly": 600_000,   "price_rs": 320},
    "d30k":   {"daily": 30_000,  "monthly": 900_000,   "price_rs": 440},
    "d50k":   {"daily": 50_000,  "monthly": 1_500_000, "price_rs": 790},
    "d100k":  {"daily": 100_000, "monthly": 3_000_000, "price_rs": 1580},
    "d150k":  {"daily": 150_000, "monthly": 4_500_000, "price_rs": 2100},
}
