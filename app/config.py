import os
from dotenv import load_dotenv

load_dotenv()

# Proxy setup
PROXY = {
    "http": f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{os.getenv('PROXY_DOMAIN')}:{os.getenv('PROXY_PORT')}",
    "https": f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{os.getenv('PROXY_DOMAIN')}:{os.getenv('PROXY_PORT')}",
}

# Paths
COOKIES_PATH = os.getenv("COOKIES_PATH", "cookies/cookies.txt")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

# Plans => daily_limit, monthly_limit
API_KEYS = {
    "FREEKEY123": (1000, 30000),
    "BASICKEY456": (5000, 150000),
    "PROKEY789": (10000, 300000),
    "ULTRAKEY000": (20000, 600000),
    "MEGAKEY111": (30000, 900000),
    "SUPERKEY222": (50000, 1500000),
    "MAXKEY333": (100000, 3000000),
    "GODKEY444": (150000, 4500000),
}
