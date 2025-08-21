import os
from fastapi import HTTPException
from datetime import datetime
from app.config import users_col
import yt_dlp

# ---------------- API Key Check ----------------
def check_api_key(key: str):
    user = users_col.find_one({"api_key": key})
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    usage = user.get("usage", {})
    today_usage = usage.get(today, 0)

    daily_limit = user.get("daily_limit", 1000)

    if today_usage >= daily_limit:
        raise HTTPException(status_code=429, detail="Daily limit reached")

    # update usage
    usage[today] = today_usage + 1
    users_col.update_one({"api_key": key}, {"$set": {"usage": usage}})
    return user


# ---------------- Media Downloader ----------------
def get_media(url: str, video: bool = False, quality: str = "720p"):
    ydl_opts = {
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "format": "bestaudio/best" if not video else f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename, info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


def save_media(file_path: str, dest_folder: str = "downloads"):
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    os.rename(file_path, dest_path)
    return dest_path
