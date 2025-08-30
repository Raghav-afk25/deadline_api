import os, yt_dlp

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
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "proxy": PROXY_URL,
        "cookiefile": COOKIES_PATH,
        "merge_output_format": "mp4",
    }

def download_audio(url):
    opts = _base_opts()
    opts.update({
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "http_headers": {"User-Agent": ANDROID_UA}
    })
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        out = ydl.prepare_filename(info).replace(".webm",".mp3")
        return out, info.get("title")

def download_video(url):
    opts = _base_opts()
    opts.update({
        "format": "bv*[height<=720][vcodec^=avc1]+ba/b[height<=720]",
        "http_headers": {"User-Agent": IOS_UA}
    })
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        out = ydl.prepare_filename(info)
        if not out.endswith(".mp4"):
            new = os.path.splitext(out)[0] + ".mp4"
            os.rename(out,new)
            out = new
        return out, info.get("title")
