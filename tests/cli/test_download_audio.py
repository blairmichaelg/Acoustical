import unittest
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.download_audio import download_audio_command

class TestDownloadAudioCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.download_audio.download_audio')
    def test_download_audio_success(self, mock_download_audio):
        mock_download_audio.return_value = "/path/to/downloaded/audio.mp3"
        url = "http://example.com/audio.mp3"
        out_dir = "test_output"

        result = self.runner.invoke(download_audio_command, [url, '--out_dir', out_dir])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Downloaded to: /path/to/downloaded/audio.mp3", result.output)
        mock_download_audio.assert_called_once_with(url, out_dir)

    @patch('cli.commands.download_audio.download_audio')
    def test_download_audio_failure(self, mock_download_audio):
        mock_download_audio.side_effect = Exception("Network error")
        url = "http://example.com/audio.mp3"

        result = self.runner.invoke(download_audio_command, [url])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Audio download failed: Network error", result.output)
        mock_download_audio.assert_called_once_with(url, 'audio_input') # Default out_dir

    @patch('cli.commands.download_audio.download_audio')
    def test_download_audio_default_out_dir(self, mock_download_audio):
        mock_download_audio.return_value = "/path/to/default/audio.mp3"
        url = "http://example.com/audio.mp3"

        result = self.runner.invoke(download_audio_command, [url])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Downloaded to: /path/to/default/audio.mp3", result.output)
        mock_download_audio.assert_called_once_with(url, 'audio_input')

if __name__ == '__main__':
    unittest.main()
