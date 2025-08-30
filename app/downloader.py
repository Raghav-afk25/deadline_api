import os, shutil, requests
from pathlib import Path
from typing import Tuple
import yt_dlp

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = ROOT_DIR / "downloads"
COOKIES_PATH = ROOT_DIR / "cookies" / "cookies.txt"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# External API config
EXT_API_URL = "https://tgmusic.fallenapi.fun"
EXT_API_KEY = "3882f1_aEYwyGw56gqPKEMfJZoOculHd3GivN8p"

# User-Agents
UA_ANDROID = "com.google.android.youtube/19.20.35 (Linux; Android 13)"
UA_IOS     = "com.google.ios.youtube/19.20.37 (iPhone15,3; iOS 17_5)"

def _yt_url(ytid: str) -> str:
    return f"https://www.youtube.com/watch?v={ytid}"

def _base_opts() -> dict:
    opts = {
        "noplaylist": True,
        "quiet": True,
        "cookiefile": str(COOKIES_PATH),
        "retries": 30,
        "fragment_retries": 30,
        "concurrent_fragment_downloads": 16,
        "nocheckcertificate": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
        "http_headers": {"User-Agent": UA_ANDROID},
    }
    if shutil.which("aria2c"):
        opts["external_downloader"] = "aria2c"
        opts["external_downloader_args"] = [
            "--max-connection-per-server=16",
            "--split=16",
            "--min-split-size=1M",
            "--allow-overwrite=true",
            "--auto-file-renaming=false",
            "--summary-interval=0",
        ]
    return opts

# -------- Try External API first --------------------------------------
def try_external_api(ytid: str, video: bool) -> str | None:
    try:
        url = f"{EXT_API_URL}/song/{ytid}"
        r = requests.get(url, params={"key": EXT_API_KEY, "video": str(video).lower()}, timeout=15)
        if r.status_code == 200:
            out = DOWNLOAD_DIR / f"{ytid}{'.mp4' if video else '.m4a'}"
            with open(out, "wb") as f:
                f.write(r.content)
            return str(out)
    except Exception as e:
        print("External API failed:", e)
    return None

# -------- Audio -------------------------------------------------------
def download_audio_by_id(ytid: str) -> Tuple[str, str]:
    out = DOWNLOAD_DIR / f"{ytid}.m4a"
    if out.exists():
        return str(out), ytid

    # 1) External API
    fast = try_external_api(ytid, video=False)
    if fast:
        return fast, ytid

    # 2) Fallback cookies yt-dlp
    opts = _base_opts()
    opts.update({
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }],
    })
    url = _yt_url(ytid)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return str(out), (info.get("title") or ytid)

# -------- Video -------------------------------------------------------
def download_video_by_id(ytid: str) -> Tuple[str, str]:
    out = DOWNLOAD_DIR / f"{ytid}.mp4"
    if out.exists():
        return str(out), ytid

    # 1) External API
    fast = try_external_api(ytid, video=True)
    if fast:
        return fast, ytid

    # 2) Fallback cookies yt-dlp
    opts = _base_opts()
    opts["http_headers"] = {"User-Agent": UA_IOS}
    opts["extractor_args"] = {"youtube": {"player_client": ["ios"]}}
    opts.update({
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "format": "bv*[vcodec^=avc1][height<=720]+ba/b[height<=720]",
    })
    url = _yt_url(ytid)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return str(out), (info.get("title") or ytid)
