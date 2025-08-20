import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "deadline_api")
API_KEY = os.getenv("API_KEY")  # baad me generate karke mongo me daalna
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["users"]
