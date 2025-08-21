# app/main.py
from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse, JSONResponse

# Telegram (blocking API; we'll run it in a thread when needed)
from telegram import Bot

# Our modules
from app.config import (
    API_KEY,
    BOT_TOKEN,
    CHANNEL_ID,
    DOWNLOAD_DIR,
)
from app.utils import get_media, save_media  # Mongo cache helpers
from app.downloader import url_from_id, download_audio, download_video


app = FastAPI(
    title="DeadlineTech API",
    version="1.0.0",
    description="Ultra-fast YouTube audio/video fetch API for Telegram music bots.",
)


# ----------------------------- helpers --------------------------------- #

def _check_api_key(key: str) -> None:
    """
    Simple API key check:
    - Allows the single global API_KEY from .env
    (If you later use per-user keys via Mongo, you can replace this.)
    """
    if not key or key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


def _upload_to_channel(file_path: str, title: str, media_type: str) -> Optional[str]:
    """
    Uploads the media to Telegram channel if BOT_TOKEN and CHANNEL_ID are set.
    Returns the Telegram file_id if uploaded, else None.
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


# ------------------------------ routes ---------------------------------- #

@app.get("/", tags=["meta"])
def root():
    return {"ok": True, "service": "DeadlineTech API"}


@app.get("/health", tags=["meta"])
def health():
    return {"ok": True}


@app.get("/song/{ytid}", tags=["media"])
def song_endpoint(
    ytid: str = Path(..., description="YouTube video ID"),
    key: str = Query(..., description="API key"),
    video: bool = Query(False, description="Return video instead of audio"),
):
    """
    Pattern:
      GET /song/{ytid}?key=<API_KEY>[&video=True]
    - Checks API key
    - Looks up cache (Mongo) → returns Telegram file_id if found
    - Downloads via yt-dlp (audio MP3 192kbps, or video 720p MP4)
    - If Telegram configured → uploads to channel, caches file_id, returns JSON
      Otherwise → serves the file directly as a download
    """
    _check_api_key(key)

    media_type = "video" if video else "audio"
    url = url_from_id(ytid)

    # 1) cache check
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

    # 2) download now
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        if media_type == "audio":
            file_path, title = download_audio(url)
        else:
            file_path, title = download_video(url)
    except Exception as e:
        # yt-dlp errors are long; pass a readable message
        raise HTTPException(
            status_code=500,
            detail=f"Download error: {e}"
        )

    # 3) if telegram configured, upload & cache; else serve file directly
    file_id = None
    try:
        file_id = _upload_to_channel(file_path, title, media_type)
    except Exception as e:
        # Don't fail the whole request if Telegram upload fails; just continue
        # and return the file directly.
        file_id = None

    # Clean up local file after we either uploaded or will serve it
    if file_id:
        # save to cache for future instant response
        save_media(url, media_type, title, file_id)
        # remove local file
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

    # Fallback: return the actual file over HTTP if telegram is not configured
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
