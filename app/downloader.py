import yt_dlp
from app.config import COOKIES_PATH

def download_song(url: str, video: bool = False):
    ydl_opts = {
        "format": "bestaudio/best" if not video else "best",
        "outtmpl": "%(title)s.%(ext)s",
    }
    if COOKIES_PATH and COOKIES_PATH.strip():
        ydl_opts["cookiefile"] = COOKIES_PATH

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
