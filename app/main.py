import os
from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import FileResponse
from app.downloader import (
    url_from_id,
    get_direct_url,
    trigger_background_download,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(ROOT_DIR, "downloads")

app = FastAPI(title="Deadline Rapchik API", version="3.0")

@app.get("/")
def root():
    return {"ok": True, "msg": "Rapchik API running"}

@app.get("/song/{ytid}")
def song(ytid: str = Path(...), video: bool = Query(False)):
    url = url_from_id(ytid)
    fpath = os.path.join(DOWNLOAD_DIR, f"{ytid}.{'mp4' if video else 'mp3'}")

    # If already cached → serve file instantly
    if os.path.exists(fpath):
        return FileResponse(fpath, filename=os.path.basename(fpath))

    # Else → get direct stream URL for instant playback
    try:
        direct_url, title = get_direct_url(url, audio=not video)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch: {e}")

    # Trigger background download to cache for future
    trigger_background_download(url, ytid, audio=not video)

    return {
        "ok": True,
        "cached": False,
        "title": title,
        "stream_url": direct_url,
        "msg": "Serving direct stream now, caching in background",
    }
