from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
import os
from pathlib import Path

from app.downloader import (
    download_audio_by_id,
    download_video_by_id,
    DOWNLOAD_DIR,
)

app = FastAPI(title="DeadlineTech Hybrid API", version="3.0")

@app.get("/")
def root():
    return {"ok": True, "msg": "Running (External API first, cookies fallback)"}

@app.get("/song/{ytid}")
def song(
    ytid: str = Path(..., description="YouTube video ID"),
    video: bool = Query(False, description="Return video instead of audio"),
):
    try:
        ext = "mp4" if video else "m4a"
        fpath = Path(DOWNLOAD_DIR) / f"{ytid}.{ext}"
        if fpath.exists():
            return FileResponse(str(fpath), filename=fpath.name)

        if video:
            fpath_str, _ = download_video_by_id(ytid)
        else:
            fpath_str, _ = download_audio_by_id(ytid)

        return FileResponse(fpath_str, filename=os.path.basename(fpath_str))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {e}")
