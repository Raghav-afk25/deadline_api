import os
import requests
import yt_dlp
from pathlib import Path

# ---------- Paths ----------
ROOT_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = ROOT_DIR / "downloads"
COOKIES_PATH = ROOT_DIR / "cookies" / "cookies.txt"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Your fast external API ----------
EXTERNAL_BASE = "https://tgmusic.fallenapi.fun"
EXTERNAL_KEY  = "3882f1_aEYwyGw56gqPKEMfJZoOculHd3GivN8p"

ANDROID_UA = "com.google.android.youtube/19.20.35 (Linux; Android 13)"
IOS_UA     = "com.google.ios.youtube/19.20.37 (iPhone15,3; iOS 17_5)"

def url_from_id(ytid: str) -> str:
    return f"https://www.youtube.com/watch?v={ytid}"

# ---------- External API (primary) ----------
def get_from_external_api(ytid: str, video: bool = False):
    """
    Try to fetch from your super-fast API.
    - Audio:  .../song/{id}?key=KEY
    - Video:  .../song/{id}?key=KEY&video=True
    Saves to downloads and returns (filepath, title-like).
    Returns None on any error so caller can fallback to yt-dlp.
    """
    try:
        params = {"key": EXTERNAL_KEY}
        if video:
            params["video"] = "True"
        url = f"{EXTERNAL_BASE}/song/{ytid}"

        # stream to disk (fast & memory-safe)
        with requests.get(url, params=params, timeout=25, stream=True) as r:
            if r.status_code != 200:
                return None
            ext = ".mp4" if video else ".m4a"
            fpath = DOWNLOAD_DIR / f"{ytid}{ext}"
            with open(fpath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 512):  # 512 KiB
                    if chunk:
                        f.write(chunk)
            # very quick title – you can enhance later
            return str(fpath), f"extapi_{ytid}"
    except Exception as e:
        print(f"[external api fail] {e}")
        return None

# ---------- yt-dlp fallback (cookies) ----------
def _base_opts():
    return {
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "cookiefile": str(COOKIES_PATH),
        "merge_output_format": "mp4",
        # speed/robustness
        "concurrent_fragment_downloads": 10,
        "fragment_retries": 20,
        "retries": 20,
        "nocheckcertificate": True,
        "source_address": "0.0.0.0",
        "http_headers": {"User-Agent": ANDROID_UA},
    }

def download_audio(yt_url: str, ytid: str):
    """
    Prefer native m4a (no convert). Falls back to bestaudio.
    Saves as {ytid}.m4a
    """
    fpath = DOWNLOAD_DIR / f"{ytid}.m4a"
    if fpath.exists():
        return str(fpath), ytid

    opts = _base_opts()
    opts.update({
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        # if bestaudio isn’t m4a, convert to m4a to keep consistent
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }],
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(yt_url, download=True)

    return str(fpath), ytid

def download_video(yt_url: str, ytid: str):
    """
    720p AVC video + audio, final mp4
    """
    fpath = DOWNLOAD_DIR / f"{ytid}.mp4"
    if fpath.exists():
        return str(fpath), ytid

    opts = _base_opts()
    opts.update({
        "http_headers": {"User-Agent": IOS_UA},
        "format": "bv*[vcodec^=avc1][height<=720]+ba/b[height<=720]",
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(yt_url, download=True)

    return str(fpath), ytid
