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
import logging
import shutil # For shutil.which

log = logging.getLogger(__name__)

def download_audio(url, out_dir="audio_input", quiet_yt_dlp=True):
    """
    Download audio from a URL (YouTube, SoundCloud, etc.) to the specified directory,
    converting to MP3 format.
    Returns the path to the downloaded MP3 file.
    Raises ImportError if yt-dlp is not installed.
    Raises FileNotFoundError if ffmpeg is not found (for MP3 conversion).
    Raises Exception for download/network errors.
    """
    try:
        import yt_dlp
    except ImportError:
        log.error("yt-dlp is not installed. Please install with 'pip install yt-dlp'.")
        raise ImportError("yt-dlp is required. Install with 'pip install yt-dlp'.")

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        log.error("ffmpeg not found in PATH. It is required for MP3 conversion.")
        raise FileNotFoundError("ffmpeg not found in PATH. It is required for MP3 conversion.")

    if not os.path.exists(out_dir):
        log.info(f"Creating output directory: {out_dir}")
        os.makedirs(out_dir)
    
    # Output template will result in an MP3 file due to postprocessor
    # yt-dlp handles naming the final file correctly with .mp3 extension.
    output_template = os.path.join(out_dir, "%(title)s.%(ext)s") 
                                   # Using %(ext)s and letting postprocessor handle final ext.
                                   # Alternatively, could force .mp3: "%(title)s.mp3"
                                   # but yt-dlp is usually good at this.

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": quiet_yt_dlp,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192", # Bitrate for MP3
        }],
        "ffmpeg_location": ffmpeg_path,
        "keepvideo": False, # Remove original downloaded file after conversion
    }
    
    log.info(f"Attempting to download and convert audio from {url} to MP3 in {out_dir}.")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # After download and postprocessing, 'filepath' should point to the final .mp3
            # For single video downloads (noplaylist=True), info itself is the video's info.
            # If 'requested_downloads' exists, it's more robust.
            final_filepath = None
            if 'requested_downloads' in info and info['requested_downloads']:
                final_filepath = info['requested_downloads'][0].get('filepath')
            elif 'filepath' in info: # Fallback for some cases
                final_filepath = info.get('filepath')
            
            if not final_filepath or not os.path.exists(final_filepath) or not final_filepath.endswith(".mp3"):
                # If path not found or not mp3, try to construct it if title and ext are updated
                log.warning(f"Could not reliably get final MP3 path from info dict (path: {final_filepath}). Trying to build from title.")
                title = info.get('title', 'downloaded_audio')
                # Sanitize title for filename (yt-dlp does this, but good to be aware)
                # For simplicity, assume ydl.prepare_filename on updated info works
                # If info['ext'] was updated to 'mp3' by postprocessor:
                if info.get('ext') == 'mp3':
                    final_filepath = ydl.prepare_filename(info) # This should give the .mp3 name
                else: # Construct it manually as a last resort
                    sanitized_title = ydl.prepare_filename({'title': title, 'ext': 'mp3'}) # Get sanitized name with .mp3
                    # Remove the directory part if prepare_filename added it based on a different outtmpl
                    base_sanitized_title = os.path.basename(sanitized_title)
                    final_filepath = os.path.join(out_dir, base_sanitized_title)

                if not os.path.exists(final_filepath):
                    log.error(f"Final MP3 file not found at expected path: {final_filepath}. Original info ext: {info.get('ext')}")
                    raise Exception(f"Downloaded audio processing to MP3 failed or file not found at {final_filepath}.")

            log.info(f"Audio downloaded and processed to: {final_filepath}")
            return final_filepath
    except yt_dlp.utils.DownloadError as de:
        log.error(f"yt-dlp download error for {url}: {de}")
        raise Exception(f"Audio download failed (yt-dlp error): {de}") from de
    except Exception as e:
        log.error(f"Audio download processing failed for {url}: {e}", exc_info=True)
        raise Exception(f"Audio download processing failed: {e}") from e

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
