# app/main.py
from __future__ import annotations

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
from telegram import Bot

from app.config import BOT_TOKEN, CHANNEL_ID, DOWNLOAD_DIR
from app.utils import get_media, save_media
from app.downloader import url_from_id, download_audio, download_video

app = FastAPI(
    title="DeadlineTech API",
    version="2.0.0",
    description="YouTube audio/video fetch API (no key required).",
)

# --------------------------- Telegram uploader ------------------------------ #
def _upload_to_channel(file_path: str, title: str, media_type: str) -> Optional[str]:
    """Upload to Telegram channel if env is set; return file_id or None."""
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
    return {"ok": True, "service": "DeadlineTech API (no key)"}

@app.get("/health", tags=["meta"])
def health():
    return {"ok": True}

# GET /song/{ytid}?video=True
@app.get("/song/{ytid}", tags=["media"])
def song_endpoint(
    ytid: str = Path(..., description="YouTube video ID"),
    video: bool = Query(False, description="Return video instead of audio"),
):
    media_type = "video" if video else "audio"
    url = url_from_id(ytid)

    # 1) cache: if already uploaded to Telegram, return file_id
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

    # 2) download now (audio: MP3 192kbps, video: 720p MP4)
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        if media_type == "audio":
            file_path, title = download_audio(url)
        else:
            file_path, title = download_video(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {e}")

    # 3) upload to Telegram (optional) -> cache -> respond
    file_id = None
    try:
        file_id = _upload_to_channel(file_path, title, media_type)
    except Exception:
        file_id = None

    if file_id:
        save_media(url, media_type, title, file_id)
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

    # 4) fallback: serve the file directly
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
