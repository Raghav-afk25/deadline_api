import os
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import FileResponse
from telegram import Bot

from app.config import BOT_TOKEN, CHANNEL_ID
from app.utils import get_media, save_media
from app.downloader import download_song   # ✅ only this now
from app.auth import check_api_key         # ✅ quota check yahi hai

app = FastAPI(title="DeadlineTech API")

@app.get("/")
async def root():
    return {"ok": True, "msg": "DeadlineTech API running"}

# Pattern: GET /song/{ytid}?key=<API_KEY>[&video=True]
@app.get("/song/{ytid}")
async def song_endpoint(
    ytid: str = Path(..., description="YouTube video ID"),
    key: str = Query(..., description="API key"),
    video: bool = Query(False, description="Return video instead of audio"),
):
    # 1) Enforce API key quotas (Mongo)
    user = check_api_key(key)   # ✅ yeh tumhara auth.py wala function use karega

    url = f"https://www.youtube.com/watch?v={ytid}"
    media_type = "video" if video else "audio"

    # 2) Cache check (Mongo -> Telegram file_id)
    cached = get_media(url, media_type)
    if cached:
        return {
            "ok": True,
            "cached": True,
            "type": media_type,
            "title": cached.get("title", ""),
            "url": url,
            "file_id": cached["file_id"],
        }

    # 3) Download now (Audio: HQ MP3, Video: 720p MP4)
    try:
        file_path = download_song(url, is_video=video)
        title = os.path.basename(file_path).rsplit(".", 1)[0]
    except Exception as e:
        raise HTTPException(500, f"download_failed: {e}")

    # 4) If Telegram is configured → upload to channel & cache; else return file directly
    if not BOT_TOKEN or not CHANNEL_ID:
        # Fallback: serve file over HTTP (no channel caching)
        return FileResponse(file_path, filename=os.path.basename(file_path))

    bot = Bot(token=BOT_TOKEN)
    try:
        if media_type == "audio":
            sent = await bot.send_audio(
                chat_id=CHANNEL_ID,
                audio=open(file_path, "rb"),
                title=title,
            )
            file_id = sent.audio.file_id
        else:
            sent = await bot.send_video(
                chat_id=CHANNEL_ID,
                video=open(file_path, "rb"),
                caption=title,
                supports_streaming=True,
            )
            file_id = sent.video.file_id
    finally:
        # Always clean local file
        try:
            os.remove(file_path)
        except Exception:
            pass

    # 5) Save to Mongo cache and respond
    save_media(url, media_type, title, file_id)
    return {
        "ok": True,
        "cached": False,
        "type": media_type,
        "title": title,
        "url": url,
        "file_id": file_id,
    }
