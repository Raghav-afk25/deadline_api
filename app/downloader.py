import os
import yt_dlp

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

def download_song(url: str, is_video: bool = False):
    """
    Download song or video from YouTube
    :param url: YouTube video URL
    :param is_video: True -> video 720p, False -> mp3 audio
    :return: dict with filename, title, duration
    """
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiefile": "cookies/cookies.txt",
        "noplaylist": True,
        "quiet": True,
    }

    if is_video:
        ydl_opts.update({
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        })
    else:
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
        filename = ydl.prepare_filename(info)

        return {
            "filename": filename,
            "title": info.get("title"),
            "duration": info.get("duration"),
        }
