# app/main.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse

# Telegram (only used if BOT_TOKEN & CHANNEL_ID are set)
from telegram import Bot

# Config & helpers
from app.config import (
    API_KEY,
    BOT_TOKEN,
    CHANNEL_ID,
    DOWNLOAD_DIR,
    users_col,   # <- Mongo collection: api_keys
)
from app.utils import get_media, save_media          # Mongo cache (url/type -> file_id)
from app.downloader import url_from_id, download_audio, download_video


app = FastAPI(
    title="DeadlineTech API",
    version="1.0.0",
    description="Ultra-fast YouTube audio/video fetch API for Telegram music bots.",
)

# ----------------------------- small utils --------------------------------- #

def _today() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _month() -> str:
    now = datetime.utcnow()
    return f"{now.year:04d}-{now.month:02d}"

# ------------------------- key + quota handling ----------------------------- #

def consume_request(key: str):
    """
    Accepts either:
      - Master API_KEY from config.py  (bypass limits)
      - A per-user key stored by the bot in Mongo (collection: api_keys)
    Enforces daily/monthly limits & expiry for per-user keys.
    Returns (ok: bool, info: dict|str)
    """
    # Master key bypass
    if key and key == API_KEY:
        return True, {"mode": "master"}

    # Per-user key path
    user = users_col.find_one({"api_key": key})
    if not user:
        return False, "invalid_key"

    if not user.get("active", True):
        return False, "banned"

    exp = user.get("expires_at")
    if isinstance(exp, datetime) and exp < datetime.utcnow():
        return False, "expired"

    # reset counters if day/month rolled over
    today = _today()
    if user.get("daily_reset_date") != today:
        user["daily_reset_date"] = today
        user["daily_count"] = 0

    month = _month()
    if user.get("month_start") != month:
        user["month_start"] = month
        user["monthly_count"] = 0

    daily_limit   = int(user.get("daily_limit", 1000))
    monthly_limit = int(user.get("monthly_limit", 30000))
    daily_count   = int(user.get("daily_count", 0))
    monthly_count = int(user.get("monthly_count", 0))

    if daily_count >= daily_limit:
        return False, "daily_quota_exceeded"
    if monthly_count >= monthly_limit:
        return False, "monthly_quota_exceeded"

    # increment usage
    user["daily_count"] = daily_count + 1
    user["monthly_count"] = monthly_count + 1
    usage = user.get("usage", {})
    usage[today] = int(usage.get(today, 0)) + 1
    user["usage"] = usage

    users_col.update_one({"_id": user["_id"]}, {"$set": {
        "daily_count": user["daily_count"],
        "monthly_count": user["monthly_count"],
        "daily_reset_date": user["daily_reset_date"],
        "month_start": user["month_start"],
        "usage": user["usage"],
    }})

    return True, {
        "mode": "user",
        "user": {
            "tg_id": user.get("tg_id"),
            "plan": user.get("plan_code"),
        }
    }

# --------------------------- Telegram uploader ------------------------------ #

def _upload_to_channel(file_path: str, title: str, media_type: str) -> Optional[str]:
    """
    Uploads media to Telegram channel if BOT_TOKEN and CHANNEL_ID are set.
    Returns Telegram file_id or None.
    """
    if not BOT_TOKEN or not CHANNEL_ID:
        return None

    bot = Bot(token=BOT_TOKEN)
    if media_type == "audio":
        with open(file_path, "rb") as f:
            sent = bot.send_audio(chat_id=CHANNEL_ID, audio=f, title=title)
            return sent.audio.file_id if sent and sent.audio else None
    else:
        with open(file_path, "rb") as f:
            sent = bot.send_video(
                chat_id=CHANNEL_ID,
                video=f,
                caption=title,
                supports_streaming=True,
            )
            return sent.video.file_id if sent and sent.video else None

# --------------------------------- routes ----------------------------------- #

@app.get("/", tags=["meta"])
def root():
    return {"ok": True, "service": "DeadlineTech API"}

@app.get("/health", tags=["meta"])
def health():
    return {"ok": True}

# Pattern: GET /song/{ytid}?key=<API_KEY>[&video=True]
@app.get("/song/{ytid}", tags=["media"])
def song_endpoint(
    ytid: str = Path(..., description="YouTube video ID"),
    key: str = Query(..., description="API key"),
    video: bool = Query(False, description="Return video instead of audio"),
):
    # 1) accept master or per-user key; enforce quotas for user keys
    ok, info = consume_request(key)
    if not ok:
        code = 429 if info in ("daily_quota_exceeded", "monthly_quota_exceeded") else 403
        raise HTTPException(code, detail=str(info))

    media_type = "video" if video else "audio"
    url = url_from_id(ytid)

    # 2) cache (Mongo → Telegram file_id)
    cached = get_media(url, media_type)
    if cached:
        return {
            "ok": True,
            "cached": True,
            "type": media_type,
            "title": cached.get("title") or "",
            "url": url,
            "file_id": cached.get("file_id"),
        }

    # 3) download now (Audio: MP3 192kbps, Video: 720p MP4)
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        if media_type == "audio":
            file_path, title = download_audio(url)
        else:
            file_path, title = download_video(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {e}")

    # 4) upload to Telegram channel (if configured) → cache → respond
    file_id = None
    try:
        file_id = _upload_to_channel(file_path, title, media_type)
    except Exception:
        file_id = None

    if file_id:
        # save to cache for instant next time
        save_media(url, media_type, title, file_id)
        # delete local file
        try:
            os.remove(file_path)
        except Exception:
            pass
        return {
            "ok": True,
            "cached": False,
            "type": media_type,
            "title": title,
            "url": url,
            "file_id": file_id,
        }

    # 5) fallback: serve file over HTTP (no Telegram cache)
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
