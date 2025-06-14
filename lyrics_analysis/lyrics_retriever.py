import logging
import re
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup
# from urllib.parse import quote # Not used, removed


log = logging.getLogger(__name__)


def _sanitize_name(name: str) -> str:
    """Sanitizes a string for use in a URL path (lowercase, alphanumeric only)."""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def parse_azlyrics_html(html_content: str, title: str, artist: str) -> Optional[str]:
    """
    Parses lyrics from AZLyrics.com HTML content.

    Args:
        html_content (str): The HTML content of the AZLyrics page.
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        Optional[str]: The extracted lyrics as a string, or None if not found.
    """
    log.info(f"Parsing AZLyrics HTML for {title} by {artist}")
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        lyrics_div = soup.find('div', class_='col-xs-12 col-lg-8 text-center')
        if lyrics_div:
            lyrics_content = None
            candidate_divs = []
            for div in lyrics_div.find_all('div', recursive=False):
                if ('class' not in div.attrs and 
                    not div.find('script') and
                    not div.find('div', class_='noprint')):
                    # Heuristic: skip known small, non-lyric divs often found at the start
                    text_check = div.get_text(separator=' ', strip=True).lower()
                    if "usage of azlyrics.com content" in text_check or \
                       "lyrics are property and copyright of their owners" in text_check or \
                       "are provided for educational purposes only" in text_check or \
                       len(text_check) < 50: # Skip very short divs
                        log.debug(f"Skipping potential non-lyrics div: {text_check[:100]}")
                        continue
                    
                    candidate_divs.append(div)

            # Prefer the longest candidate div, as lyrics are usually substantial
            if candidate_divs:
                best_candidate = None
                max_len = -1
                for div in candidate_divs:
                    current_text = div.get_text(separator='\n').strip()
                    if len(current_text) > max_len:
                        max_len = len(current_text)
                        best_candidate = current_text
                lyrics_content = best_candidate

            if lyrics_content:
                # Remove any common AZLyrics disclaimers
                lyrics_content = re.sub(
                    r'Embed\s*Share\s*Url:.*', '', lyrics_content, flags=re.DOTALL
                )
                lyrics_content = re.sub(r'\(\d+ translations?\)', '', lyrics_content)
                lyrics_content = re.sub(r'\[.*?\]', '', lyrics_content) # Removes [Chorus] etc.
                
                # Convert multiple spaces to a single space (e.g., left by [Chorus] removal)
                lyrics_content = re.sub(r' {2,}', ' ', lyrics_content)

                # Normalize newlines and strip each line
                lines = [line.strip() for line in lyrics_content.split('\n')]
                # Filter out any lines that are now completely empty AFTER stripping,
                # to handle cases like <br> <br> creating multiple empty strings.
                # We want to preserve intentional single blank lines between stanzas if they result from <br>\n<br>.
                # A simple approach: join, then normalize multiple newlines, then final strip.
                lyrics_content = '\n'.join(lines)
                lyrics_content = re.sub(r'\n{3,}', '\n\n', lyrics_content) # Reduce 3+ newlines to 2

                return lyrics_content.strip() # Final strip of the whole block

        log.warning(f"Could not find lyrics div for {title} by {artist}")
        return None

    except Exception as e:
        log.error(f"Error parsing AZLyrics HTML for {title} by {artist}: {e}")
        return None


def get_lyrics_from_url_or_metadata(
    url: Optional[str] = None,
    title: Optional[str] = None,
    artist: Optional[str] = None
) -> Dict[str, Any]:
    """
    Prepares information for lyrics retrieval.
    This function does NOT fetch content directly but provides the URL/metadata
    needed for an external fetcher (like an MCP tool).

    Args:
        url (str, optional): The URL of the song (e.g., YouTube URL).
        title (str, optional): The title of the song.
        artist (str, optional): The artist of the song.

    Returns:
        Dict[str, Any]: A dictionary indicating the retrieval method and parameters.
                        Example: {"method": "scrape_azlyrics", "title": "Song", "artist": "Artist"}
                        Or: {"method": "placeholder_url", "url": "http://..."}
                        Returns {"error": "message"} if no valid input.
    """
    if title and artist:
        sanitized_artist = _sanitize_name(artist)
        sanitized_title = _sanitize_name(title)
        azlyrics_url = (
            f"https://www.azlyrics.com/lyrics/{sanitized_artist}/{sanitized_title}.html"
        )
        log.info(f"Prepared AZLyrics URL for scraping: {azlyrics_url}")
        return {
            "method": "scrape_azlyrics",
            "url": azlyrics_url,
            "title": title,
            "artist": artist
        }
    elif url:
        log.info(f"Prepared URL for direct lyrics retrieval: {url}")
        return {
            "method": "placeholder_url",
            "url": url
        }
    else:
        log.warning("No valid input provided for lyrics retrieval.")
        return {"error": "Please provide a URL or a song title and artist."}
