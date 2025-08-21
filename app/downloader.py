# app/downloader.py
import os
import yt_dlp
from app.config import COOKIES_PATH, DOWNLOAD_DIR, PROXY_URL

ANDROID_UA = (
    "com.google.android.youtube/19.20.35 (Linux; U; Android 13) gzip"
)
IOS_UA = (
    "com.google.ios.youtube/19.20.37 (iPhone15,3; U; CPU iOS 17_5 like Mac OS X)"
)

def url_from_id(ytid: str) -> str:
    return f"https://www.youtube.com/watch?v={ytid}"

def _base_opts():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "proxy": PROXY_URL or None,
        "retries": 3,
        "fragment_retries": 3,
        "skip_unavailable_fragments": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }
    if COOKIES_PATH and os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts

def _client_opts(client: str):
    # client in {"android","ios","mweb"}
    if client == "android":
        return {
            "extractor_args": {"youtube": {"player_client": "android"}},
            "http_headers": {"User-Agent": ANDROID_UA, "Accept-Language": "en-US,en;q=0.9"},
        }
    if client == "ios":
        return {
            "extractor_args": {"youtube": {"player_client": "ios"}},
            "http_headers": {"User-Agent": IOS_UA, "Accept-Language": "en-US,en;q=0.9"},
        }
    return {  # mweb
        "extractor_args": {"youtube": {"player_client": "mweb"}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

def _try_download(url: str, fmt: str, client: str):
    opts = _base_opts()
    opts.update(_client_opts(client))
    opts.update({"format": fmt})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
        title = info.get("title") or "media"
        return path, title

def download_audio(url: str):
    # Prefer best audio; final file MP3 192 kbps
    fmt = "bestaudio/best"
    post = [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]

    for client in ("android", "ios", "mweb"):
        try:
            opts = _base_opts()
            opts.update(_client_opts(client))
            opts.update({"format": fmt, "postprocessors": post})
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                out = ydl.prepare_filename(info)
                if not out.lower().endswith(".mp3"):
                    out = os.path.splitext(out)[0] + ".mp3"
                title = info.get("title") or "audio"
                return out, title
        except Exception as e:
            last_err = e
            continue
    raise last_err  # type: ignore[name-defined]

def download_video(url: str):
    # 720p cap; prefer H.264 (avc1) to avoid weird codecs on some clients
    fmt = "bv*[height<=720][vcodec^=avc1]+ba/b[height<=720]"
    last_err = None
    for client in ("android", "ios", "mweb"):
        try:
            path, title = _try_download(url, fmt, client)
            # Ensure .mp4 if merged as mkv
            if not path.lower().endswith(".mp4"):
                new = os.path.splitext(path)[0] + ".mp4"
                if os.path.exists(path):
                    try:
                        os.replace(path, new)
                    except Exception:
                        pass
                path = new
            return path, title
        except Exception as e:
            last_err = e
            continue
    raise last_err
