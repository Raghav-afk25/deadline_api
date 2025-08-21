# app/config.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env
load_dotenv()

# Telegram + API configs
API_ID = os.getenv("API_ID")                # Telegram API ID
API_HASH = os.getenv("API_HASH")            # Telegram API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN")          # Telegram Bot Token
MONGO_URI = os.getenv("MONGO_URI")          # MongoDB URI
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")  # JWT / Auth secret key

# Channel ID (jaha songs/videos forward honge)
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))

# Download configs
COOKIES_PATH = os.getenv("COOKIES_PATH", "cookies/cookies.txt")  # cookies ka path
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")            # temp download dir

# MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["deadline_db"]

# Collections
users_col = db["users"]        # yaha plans aur users store honge
requests_col = db["requests"]  # yaha request logs store honge
