import os
from dotenv import load_dotenv

# Load environment from repo root ".env"
load_dotenv()

# ---------- Telegram (make bot admin in this channel) ----------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Private channel numeric id with minus, e.g. -1001234567890
try:
    TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID", "0"))
except ValueError:
    TELEGRAM_CHANNEL_ID = 0

# ---------- MongoDB (used by app.utils) ----------
# Example: mongodb://localhost:27017/  OR Atlas URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.getenv("MONGO_DB", "deadline_api")

# ---------- Proxy / Cookies / Paths ----------
PROXY_HOST = os.getenv("PROXY_HOST", "")
PROXY_PORT = os.getenv("PROXY_PORT", "")
PROXY_USER = os.getenv("PROXY_USER", "")
PROXY_PASS = os.getenv("PROXY_PASS", "")
PROXY_URL = (
    f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    if PROXY_HOST and PROXY_PORT and PROXY_USER and PROXY_PASS else None
)

# Absolute or relative path allowed (default: cookies/cookies.txt)
COOKIES_PATH = os.getenv(
    "COOKIES_PATH",
    os.path.join(os.getcwd(), "cookies", "cookies.txt")
)

# Download dir for temporary files
DOWNLOAD_DIR = os.getenv(
    "DOWNLOAD_DIR",
    os.path.join(os.getcwd(), "downloads")
)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- (Optional) Plan presets for reference ----------
# These are for your admin tooling; actual limits live per key in Mongo.
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
