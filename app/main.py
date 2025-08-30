from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
import os

from app.downloader import (
    url_from_id,
    get_from_external_api,
    download_audio,
    download_video,
    DOWNLOAD_DIR,
)

app = FastAPI(title="DeadlineTech Hybrid API", version="1.0")

@app.get("/")
def root():
    return {"ok": True, "msg": "Hybrid (External API + Cookies) running"}

@app.get("/song/{ytid}")
def song(
    ytid: str = Path(..., description="YouTube video ID"),
    video: bool = Query(False, description="If true, returns mp4 720p"),
):
    # serve from local cache if already downloaded
    ext = "mp4" if video else "m4a"
    fpath = os.path.join(DOWNLOAD_DIR, f"{ytid}.{ext}")
    if os.path.exists(fpath):
        return FileResponse(fpath, filename=os.path.basename(fpath))

    yt_url = url_from_id(ytid)

    # 1) Try your external super-fast API first
    got = get_from_external_api(ytid, video=video)
    if got:
        fpath, _ = got
        return FileResponse(fpath, filename=os.path.basename(fpath))

    # 2) Fallback to yt-dlp + cookies
    try:
        if video:
            fpath, _ = download_video(yt_url, ytid)
        else:
            fpath, _ = download_audio(yt_url, ytid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")

    return FileResponse(fpath, filename=os.path.basename(fpath))
