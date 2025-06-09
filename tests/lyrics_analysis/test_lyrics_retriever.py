import unittest
from unittest.mock import patch # MagicMock and logging not directly used by tests

from lyrics_analysis.lyrics_retriever import (
    _sanitize_name,
    parse_azlyrics_html,
    get_lyrics_from_url_or_metadata
)

# Suppress logging for most tests to keep output clean, enable for debugging if needed
# logging.disable(logging.CRITICAL)

class TestLyricsRetriever(unittest.TestCase):

    def test__sanitize_name(self):
        self.assertEqual(_sanitize_name("Test Artist!"), "testartist")
        self.assertEqual(_sanitize_name("Song Title 123"), "songtitle123")
        self.assertEqual(_sanitize_name("AlreadySanitized"), "alreadysanitized")
        self.assertEqual(_sanitize_name("With-Hyphen"), "withhyphen")
        self.assertEqual(_sanitize_name("  Spaces  "), "spaces")

    def test_parse_azlyrics_html_success(self):
        # Unused variables html_fixture, expected_lyrics, expected_lyrics_after_parse removed.
        # The refined fixture and expected output are what matters.
        html_fixture_refined = """
        <html><body>
        <div class="col-xs-12 col-lg-8 text-center">
            <div>Usage of azlyrics.com content is permitted for personal or educational use only.</div>
            <div> <!-- This div is chosen by the parser logic -->
                Line 1 of the song<br>
                Line 2 with [Chorus] annotation<br>
                Line 3.
                <br><br> <!-- These might become newlines depending on get_text separator -->
                Submit Corrections 
            </div>
            <div class="noprint">Ads</div>
            <!-- Embed Share Url and translations are usually outside the main lyrics text block or handled by regex -->
        </div>
        </body></html>
        """
        # After div.get_text(separator='\n').strip():
        # "Line 1 of the song\nLine 2 with [Chorus] annotation\nLine 3.\n\nSubmit Corrections"
        # After re.sub(r'\[.*?\]', '', lyrics_content):
        # "Line 1 of the song\nLine 2 with annotation\nLine 3.\n\nSubmit Corrections"
        # The other regexes for Embed/translations won't match this specific text.
        expected_lyrics_from_fixture = "Line 1 of the song\nLine 2 with annotation\nLine 3.\n\nSubmit Corrections"


        lyrics = parse_azlyrics_html(html_fixture_refined, "Test Song", "Test Artist")
        self.assertEqual(lyrics, expected_lyrics_from_fixture)

    def test_parse_azlyrics_html_lyrics_not_found_no_target_div(self):
        html_fixture = "<html><body><div>No lyrics here</div></body></html>"
        lyrics = parse_azlyrics_html(html_fixture, "Test Song", "Test Artist")
        self.assertIsNone(lyrics)

    def test_parse_azlyrics_html_lyrics_not_found_empty_div(self):
        html_fixture = """
        <html><body>
        <div class="col-xs-12 col-lg-8 text-center">
            <div><!-- Empty --></div>
        </div>
        </body></html>
        """
        lyrics = parse_azlyrics_html(html_fixture, "Test Song", "Test Artist")
        self.assertIsNone(lyrics) # Parser looks for a div *without* class inside the main one

    def test_parse_azlyrics_html_parser_exception(self):
        with patch('bs4.BeautifulSoup', side_effect=Exception("BS parsing failed")):
            lyrics = parse_azlyrics_html("<html></html>", "Test Song", "Test Artist")
            self.assertIsNone(lyrics)

    def test_get_lyrics_from_url_or_metadata_with_title_artist(self):
        result = get_lyrics_from_url_or_metadata(title="Song Title", artist="Artist Name")
        self.assertEqual(result["method"], "scrape_azlyrics")
        self.assertEqual(result["title"], "Song Title")
        self.assertEqual(result["artist"], "Artist Name")
        self.assertTrue("artistname/songtitle.html" in result["url"])

    def test_get_lyrics_from_url_or_metadata_with_url_only(self):
        test_url = "http://example.com/lyrics"
        result = get_lyrics_from_url_or_metadata(url=test_url)
        self.assertEqual(result["method"], "placeholder_url")
        self.assertEqual(result["url"], test_url)
        self.assertNotIn("title", result)
        self.assertNotIn("artist", result)

    def test_get_lyrics_from_url_or_metadata_no_input(self):
        result = get_lyrics_from_url_or_metadata()
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Please provide a URL or a song title and artist.")

    def test_get_lyrics_from_url_or_metadata_partial_input_title_only(self):
        result = get_lyrics_from_url_or_metadata(title="Song Title")
        self.assertIn("error", result) # Should require artist too for AZLyrics
        self.assertEqual(result["error"], "Please provide a URL or a song title and artist.")


    def test_get_lyrics_from_url_or_metadata_partial_input_artist_only(self):
        result = get_lyrics_from_url_or_metadata(artist="Artist Name")
        self.assertIn("error", result) # Should require title too for AZLyrics
        self.assertEqual(result["error"], "Please provide a URL or a song title and artist.")

if __name__ == '__main__':
    unittest.main()
