import click
import sys
from common.utils import format_error, serialize_result
from lyrics_analysis.lyrics_retriever import get_lyrics_from_url_or_metadata


@click.command("get-lyrics")
@click.option(
    '--url', type=str,
    help='URL of the song (e.g., YouTube) to retrieve lyrics for.'
)
@click.option('--title', type=str, help='Title of the song.')
@click.option('--artist', type=str, help='Artist of the song.')
def get_lyrics_command(url, title, artist):  # Removed async
    """
    Retrieve lyrics for a song using a URL or by providing title and artist.
    """
    try:
        if not (url or (title and artist)):
            click.echo(
                format_error(
                    "Missing URL or song title/artist.",
                    "Please provide either a --url or both --title and --artist."
                ),
                err=True
            )
            sys.exit(1)

        lyrics_info = get_lyrics_from_url_or_metadata(
            url=url, title=title, artist=artist
        )

        # Simplified logic: get_lyrics_from_url_or_metadata should handle
        # fetching or return placeholders.
        # No direct MCP tool interaction from CLI for now.
        if lyrics_info.get("lyrics_text"):  # Safely check if lyrics_text exists
            source = lyrics_info.get("method", "unknown")
            payload = {
                "lyrics": lyrics_info["lyrics_text"],
                "source": source
            }
            click.echo(serialize_result(payload))
        elif lyrics_info.get("method") == "scrape_azlyrics":
            # This CLI command currently does not fetch/parse from AZLyrics.
            # It only prepares the URL.
            msg_main = "AZLyrics retrieval not implemented in CLI."
            prepared_url = lyrics_info.get('url', 'N/A')
            msg_detail = (
                f"Prepared URL: {prepared_url}. "
                "Manual fetching/parsing needed."
            )
            full_error_message = f"{msg_main} {msg_detail}"
            click.echo(format_error(full_error_message), err=True)
            sys.exit(1)
        elif lyrics_info.get("method") == "placeholder_url":
            lyrics_text = (
                f"Lyrics for song from URL: {lyrics_info['url']}\n\n"
                "(Placeholder lyrics: Verse 1...\nChorus...\nVerse 2...)"
            )
            payload = {"lyrics": lyrics_text, "source": "placeholder_url"}
            click.echo(serialize_result(payload))
        else:
            method_info = lyrics_info.get('method', 'N/A')
            msg_main = "Unknown lyrics retrieval method or no lyrics found."
            msg_detail = f"Method: {method_info}"
            click.echo(format_error(msg_main, msg_detail), err=True)
            sys.exit(1)

    except Exception as e:
        msg_main = "An unexpected error occurred during lyrics retrieval."
        # Here, 'e' is a genuine Exception object, so passing it as exc is correct.
        click.echo(format_error(msg_main, exc=e), err=True)
        sys.exit(1)
