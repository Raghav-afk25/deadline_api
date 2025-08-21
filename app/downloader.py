# app/downloader.py
import os
import yt_dlp
from app.config import COOKIES_PATH, DOWNLOAD_DIR, PROXY_URL

def url_from_id(ytid: str) -> str:
    return f"https://www.youtube.com/watch?v={ytid}"

def _common_opts():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "proxy": PROXY_URL,  # ← हमेशा proxy से
        "http_headers": {    # real browser headers
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        "extractor_args": {
            # Android client अक्सर challenge कम करता है
            "youtube": {"player_client": ["android"]},
        },
        "retries": 3,
        "fragment_retries": 3,
        "skip_unavailable_fragments": True,
        "nocheckcertificate": True,
    }
    # cookies दें तो use करेगा; file missing हो तो skip (crash नहीं)
    if COOKIES_PATH and os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts

def download_audio(url: str):
    ydl_opts = _common_opts()
    ydl_opts.update({
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        out = ydl.prepare_filename(info)
        if not out.lower().endswith(".mp3"):
            out = os.path.splitext(out)[0] + ".mp3"
        return out, info.get("title") or "audio"

def download_video(url: str):
    ydl_opts = _common_opts()
    ydl_opts.update({
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "merge_output_format": "mp4",
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        out = ydl.prepare_filename(info)
        if not out.lower().endswith(".mp4"):
            out = os.path.splitext(out)[0] + ".mp4"
        return out, info.get("title") or "video"
