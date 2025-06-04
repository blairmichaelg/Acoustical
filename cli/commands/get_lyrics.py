import click
import sys
from common.utils import format_error, serialize_result
from lyrics_analysis.lyrics_retriever import get_lyrics_from_url_or_metadata, parse_azlyrics_html

@click.command()
@click.option(
    '--url', type=str, help='URL of the song (e.g., YouTube URL) to retrieve lyrics for.'
)
@click.option('--title', type=str, help='Title of the song.')
@click.option('--artist', type=str, help='Artist of the song.')
async def get_lyrics_cli(url, title, artist):
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

        lyrics_info = get_lyrics_from_url_or_metadata(url=url, title=title, artist=artist)

        if lyrics_info["method"] == "scrape_azlyrics":
            try:
                # The agent will inject the `use_mcp_tool` function.
                html_content = await use_mcp_tool(  # pylint: disable=undefined-variable
                    server_name="github.com/zcaceres/fetch-mcp",
                    tool_name="fetch_html",
                    arguments={"url": lyrics_info["url"]}
                )
                lyrics_text = parse_azlyrics_html(
                    html_content, lyrics_info["title"], lyrics_info["artist"]
                )
                if lyrics_text:
                    click.echo(
                        serialize_result({"lyrics": lyrics_text, "source": "azlyrics.com"})
                    )
                else:
                    click.echo(
                        format_error(
                            "Failed to retrieve lyrics from AZLyrics.",
                            "Could not parse lyrics from the page."
                        ),
                        err=True
                    )
                    sys.exit(1)
            except Exception as e:
                click.echo(format_error("Error fetching lyrics from AZLyrics.", e), err=True)
                sys.exit(1)
        elif lyrics_info["method"] == "placeholder_url":
            lyrics_text = (
                f"Lyrics for song from URL: {lyrics_info['url']}\n\n"
                "(Placeholder lyrics: Verse 1...\nChorus...\nVerse 2...)"
            )
            click.echo(
                serialize_result({"lyrics": lyrics_text, "source": "placeholder_url"})
            )
        else:
            click.echo(
                format_error(
                    "Unknown lyrics retrieval method.",
                    f"Method: {lyrics_info['method']}"
                ),
                err=True
            )
            sys.exit(1)

    except Exception as e:
        click.echo(format_error("An unexpected error occurred during lyrics retrieval", e), err=True)
        sys.exit(1)
