from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from app.utils import check_rate_limit
from app.downloader import download_song

app = FastAPI(title="Deadline YouTube API")

@app.get("/song/{ytid}")
async def get_song(ytid: str, key: str = Query(...), video: bool = False):
    # check API key + rate limit
    check_rate_limit(key)

    url = f"https://www.youtube.com/watch?v={ytid}"
    file_path = download_song(url, video)

    return FileResponse(path=file_path, filename=file_path.split("/")[-1])
