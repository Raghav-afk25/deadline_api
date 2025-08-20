from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from app.utils import check_api_key
from app.downloader import download_song
from app.plans import PLANS

app = FastAPI(title="DeadlineTech API")

@app.get("/")
def root():
    return {"status": "running", "plans": PLANS}

@app.get("/song/{video_id}")
def get_song(video_id: str, key: str = Query(...), video: bool = False):
    user = check_api_key(key)
    url = f"https://www.youtube.com/watch?v={video_id}"
    file_path = download_song(url, is_video=video)
    return FileResponse(file_path, filename=file_path.split("/")[-1])
