import os, yt_dlp, threading

ANDROID_UA = "com.google.android.youtube/19.20.35 (Linux; Android 13)"
IOS_UA     = "com.google.ios.youtube/19.20.37 (iPhone15,3; iOS 17_5)"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_PATH = os.path.join(ROOT_DIR, "cookies", "cookies.txt")
DOWNLOAD_DIR = os.path.join(ROOT_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PROXY_URL = "http://zclarjnk-rotate:83fjqnfinvpm@p.webshare.io:80"

def url_from_id(ytid): 
    return f"https://www.youtube.com/watch?v={ytid}"

def _base_opts():
    return {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "proxy": PROXY_URL,
        "cookiefile": COOKIES_PATH,
        "merge_output_format": "mp4",
        "concurrent_fragment_downloads": 5,
        "fragment_retries": 10,
        "retries": 10,
        "source_address": "0.0.0.0",
        "prefer_insecure": True,
    }

# ---- Direct URL (for instant playback) ---- #
def get_direct_url(url, audio=True):
    opts = _base_opts()
    opts.pop("outtmpl")  # not saving
    if audio:
        opts["format"] = "bestaudio/best"
        opts["http_headers"] = {"User-Agent": ANDROID_UA}
    else:
        opts["format"] = "bv*[height<=720][vcodec^=avc1]+ba/b[height<=720]"
        opts["http_headers"] = {"User-Agent": IOS_UA}

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"], info.get("title") or "media"

# ---- Background download (for cache) ---- #
def _bg_download(url, ytid, audio=True):
    try:
        fpath = os.path.join(DOWNLOAD_DIR, f"{ytid}.{'mp3' if audio else 'mp4'}")
        if os.path.exists(fpath): return  # already cached
        opts = _base_opts()
        if audio:
            opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }],
                "outtmpl": fpath,
                "http_headers": {"User-Agent": ANDROID_UA},
            })
        else:
            opts.update({
                "format": "bv*[height<=720][vcodec^=avc1]+ba/b[height<=720]",
                "outtmpl": fpath,
                "http_headers": {"User-Agent": IOS_UA},
            })
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        print(f"[bg_download error] {e}")

def trigger_background_download(url, ytid, audio=True):
    t = threading.Thread(target=_bg_download, args=(url, ytid, audio))
    t.daemon = True
    t.start()
