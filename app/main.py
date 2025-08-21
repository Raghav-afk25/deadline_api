import os
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import FileResponse
from telegram import Bot

from app.config import BOT_TOKEN, CHANNEL_ID
from app.utils import consume_request, get_media, save_media
from app.downloader import url_from_id, download_audio, download_video

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
    ok, info = consume_request(key)
    if not ok:
        code = 429 if info in ("daily_quota_exceeded", "monthly_quota_exceeded") else 403
        raise HTTPException(code, detail=str(info))

    url = url_from_id(ytid)
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
        if media_type == "audio":
            file_path, title = download_audio(url)
        else:
            file_path, title = download_video(url)
    except Exception as e:
        raise HTTPException(500, f"download_failed: {e}")

    # 4) If Telegram is configured → upload to channel & cache; else return file directly
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        # Fallback: serve file over HTTP (no channel caching)
        return FileResponse(file_path, filename=os.path.basename(file_path))

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        if media_type == "audio":
            sent = await bot.send_audio(
                chat_id=TELEGRAM_CHANNEL_ID,
                audio=open(file_path, "rb"),
                title=title,
            )
            file_id = sent.audio.file_id
        else:
            sent = await bot.send_video(
                chat_id=TELEGRAM_CHANNEL_ID,
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
