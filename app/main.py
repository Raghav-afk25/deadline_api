import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from app.utils import RateLimiter
from app.downloader import download_from_youtube
from app.config import API_KEYS

app = FastAPI(title="DeadlineTech API")
limiter = RateLimiter()

@app.middleware("http")
async def check_rate_limit(request: Request, call_next):
    key = request.query_params.get("key")
    if not key or key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    if not limiter.allow_request(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for your plan")

    return await call_next(request)

@app.get("/song/{video_id}")
async def get_song(video_id: str, key: str = Query(...), video: bool = False):
    try:
        file_path = download_from_youtube(video_id, video=video)
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "Deadline API is running 🚀"}
