import os
from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import FileResponse
from app.downloader import url_from_id, download_audio, download_video

app = FastAPI(title="Deadline Direct API", version="1.0")

@app.get("/")
def root():
    return {"ok": True, "msg": "Direct download API running"}

@app.get("/song/{ytid}")
def song(ytid: str = Path(...), video: bool = Query(False)):
    url = url_from_id(ytid)
    try:
        if video:
            path, title = download_video(url)
        else:
            path, title = download_audio(url)
    except Exception as e:
        raise HTTPException(500, f"Download failed: {e}")

    filename = os.path.basename(path)
    return FileResponse(path, filename=filename, media_type="application/octet-stream")
