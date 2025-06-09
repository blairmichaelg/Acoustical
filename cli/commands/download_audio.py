import click
from audio_input.downloader import download_audio

@click.command("download-audio") # Renamed command
@click.argument('url')
@click.option('--out_dir', default='audio_input', help='Output directory for downloaded audio')
def download_audio_command(url, out_dir): # Renamed function
    """Download audio from a URL (YouTube, SoundCloud, etc.) to audio_input/."""
    try:
        path = download_audio(url, out_dir)
        click.echo(f"Downloaded to: {path}")
    except Exception as e:
        raise click.ClickException(f"Audio download failed: {e}")
