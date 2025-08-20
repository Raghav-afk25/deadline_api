import os
import yt_dlp
from app.config import COOKIES_PATH, DOWNLOAD_DIR, PROXY

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_from_youtube(video_id: str, video: bool = False) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    outtmpl = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best" if not video else "best",
        "outtmpl": outtmpl,
        "cookiefile": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        "proxy": PROXY["http"],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
