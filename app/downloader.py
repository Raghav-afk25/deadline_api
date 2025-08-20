import yt_dlp

def download_song(url: str, is_video: bool = False):
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
        return ydl.prepare_filename(info)
