import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# ========= Telegram =========
BOT_TOKEN  = os.getenv("BOT_TOKEN", "7638651872:AAHN3nTAeNNFh9pcG5UP2dXXMM_FUjEmC1s")
OWNER_ID   = int(os.getenv("OWNER_ID", "8162844043"))   # <- Tumhara Owner ID
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002530157716"))

# ========= MongoDB =========
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://smaug571:ZENeRk1gAJhkmaXc@cluster0.ebgdwyo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
MONGO_DB  = os.getenv("DB_NAME", "cluster0")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
users_col = db["api_keys"]

# ========= API Master Key =========
API_KEY = os.getenv("API_KEY", "supersecret")

# ========= Plans =========
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

# ========= Downloader paths =========
COOKIES_PATH = os.getenv("COOKIES_PATH", os.path.join(os.getcwd(), "cookies", "cookies.txt"))
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ========= Sanity log =========
def _print_config_summary():
    print("[config] Mongo DB:", MONGO_DB)
    print("[config] users_col:", users_col.name)
    print("[config] BOT_TOKEN set?:", bool(BOT_TOKEN))
    print("[config] OWNER_ID:", OWNER_ID)
    print("[config] CHANNEL_ID:", CHANNEL_ID)
    print("[config] API_KEY:", API_KEY)
# _print_config_summary()
