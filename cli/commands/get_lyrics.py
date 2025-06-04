import click
import sys
from lyrics_analysis.lyrics_retriever import get_lyrics
from common.utils import format_error, serialize_result

@click.command()
@click.option('--url', type=str, help='URL of the song (e.g., YouTube URL) to retrieve lyrics for.')
@click.option('--title', type=str, help='Title of the song.')
@click.option('--artist', type=str, help='Artist of the song.')
def get_lyrics_cli(url, title, artist):
    """
    Retrieve lyrics for a song using a URL or by providing title and artist.
    """
    try:
        if not (url or (title and artist)):
            click.echo(format_error("Missing URL or song title/artist.", "Please provide either a --url or both --title and --artist."), err=True)
            sys.exit(1)

        lyrics_data = get_lyrics(url=url, title=title, artist=artist)

        if "error" in lyrics_data:
            click.echo(format_error("Lyrics retrieval failed", lyrics_data['error']), err=True)
            sys.exit(1)
        
        click.echo(serialize_result({"lyrics": lyrics_data.get("lyrics", "")}))
    except Exception as e:
        click.echo(format_error("An unexpected error occurred during lyrics retrieval", e), err=True)
        sys.exit(1)
