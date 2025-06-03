"""
Audio downloader utility for Acoustic Cover Assistant.

Supports downloading audio from YouTube and other sites using yt-dlp.
Requires yt-dlp to be installed (`pip install yt-dlp`).

Usage:
    from audio_input.downloader import download_audio
    download_audio("https://www.youtube.com/watch?v=...", out_dir="audio_input")

Command-line usage:
    python audio_input/downloader.py <url> [--out_dir audio_input]

"""

import os
import sys

def download_audio(url, out_dir="audio_input"):
    """
    Download audio from a URL (YouTube, SoundCloud, etc.) to the specified directory.
    Returns the path to the downloaded file.
    Raises ImportError if yt-dlp is not installed.
    Raises Exception for download/network errors.
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required. Install with 'pip install yt-dlp'.")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Replace extension with .mp3 if postprocessing
            if filename.endswith(".webm") or filename.endswith(".m4a"):
                filename = os.path.splitext(filename)[0] + ".mp3"
            return filename
    except Exception as e:
        raise Exception(f"Audio download failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download audio from a URL (YouTube, SoundCloud, etc.)")
    parser.add_argument("url", help="URL to download audio from")
    parser.add_argument("--out_dir", default="audio_input", help="Output directory")
    args = parser.parse_args()
    try:
        path = download_audio(args.url, args.out_dir)
        print(f"Downloaded to: {path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
