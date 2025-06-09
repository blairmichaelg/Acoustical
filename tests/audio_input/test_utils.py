import unittest
from unittest.mock import patch 
# Removed MagicMock as it's not directly used, os is also not directly used by tests

# Assuming utils.py is in audio_input directory, and tests are run from project root
from audio_input import utils as audio_utils 
# Import constants from config directly for mocking or reference if needed
# For this test, we'll mostly mock the constants where they are used or the functions that use them.

class TestAudioUtils(unittest.TestCase):

    @patch('audio_input.utils.ALLOWED_EXTENSIONS', {'.mp3', '.wav'})
    def test_is_allowed_audio_file(self):
        self.assertTrue(audio_utils.is_allowed_audio_file("song.mp3"))
        self.assertTrue(audio_utils.is_allowed_audio_file("track.wav"))
        self.assertTrue(audio_utils.is_allowed_audio_file("UPPER.MP3"))
        self.assertFalse(audio_utils.is_allowed_audio_file("document.txt"))
        self.assertFalse(audio_utils.is_allowed_audio_file("archive.zip"))
        self.assertFalse(audio_utils.is_allowed_audio_file("no_extension"))
        self.assertFalse(audio_utils.is_allowed_audio_file("image.jpeg"))

    @patch('mimetypes.guess_type')
    def test_is_valid_audio_mime(self, mock_guess_type):
        mock_guess_type.return_value = ("audio/mpeg", None)
        self.assertTrue(audio_utils.is_valid_audio_mime("song.mp3"))

        mock_guess_type.return_value = ("audio/wav", None)
        self.assertTrue(audio_utils.is_valid_audio_mime("track.wav"))

        mock_guess_type.return_value = ("text/plain", None)
        self.assertFalse(audio_utils.is_valid_audio_mime("notes.txt"))

        mock_guess_type.return_value = ("application/pdf", None)
        self.assertFalse(audio_utils.is_valid_audio_mime("doc.pdf"))
        
        mock_guess_type.return_value = (None, None) # Unknown type
        self.assertFalse(audio_utils.is_valid_audio_mime("unknown.dat"))

    @patch('os.path.exists') # This mock will be passed as mock_os_path_exists
    @patch('os.path.getsize') # This mock will be passed as mock_os_path_getsize
    @patch('audio_input.utils.MAX_FILE_SIZE_MB', 10) # This patches the constant, doesn't pass an arg
    def test_is_file_size_ok(self, mock_os_path_getsize, mock_os_path_exists): # Corrected argument order
        # Test file below limit
        mock_os_path_exists.return_value = True
        mock_os_path_getsize.return_value = 5 * 1024 * 1024  # 5 MB
        # Test against the patched MAX_FILE_SIZE_MB (10) by passing it explicitly
        self.assertTrue(audio_utils.is_file_size_ok("small_file.mp3", max_mb=10))

        # Test file at limit
        mock_os_path_getsize.return_value = 10 * 1024 * 1024  # 10 MB
        self.assertTrue(audio_utils.is_file_size_ok("limit_file.mp3", max_mb=10))

        # Test file above limit
        mock_os_path_getsize.return_value = 11 * 1024 * 1024  # 11 MB
        self.assertFalse(audio_utils.is_file_size_ok("large_file.mp3", max_mb=10))

        # Test non-existent file (max_mb doesn't matter here as it returns False early)
        mock_os_path_exists.return_value = False
        # mock_os_path_getsize will not be called if exists is False, but set it for completeness if it were
        mock_os_path_getsize.return_value = 0 
        self.assertFalse(audio_utils.is_file_size_ok("non_existent.mp3"))
        
        # Test with custom max_mb
        mock_os_path_exists.return_value = True
        mock_os_path_getsize.return_value = 2 * 1024 * 1024 # 2MB
        self.assertTrue(audio_utils.is_file_size_ok("custom_limit_ok.mp3", max_mb=2))
        self.assertFalse(audio_utils.is_file_size_ok("custom_limit_bad.mp3", max_mb=1))


    @patch('os.path.isfile')
    @patch('audio_input.utils.is_allowed_audio_file')
    @patch('audio_input.utils.is_valid_audio_mime')
    @patch('audio_input.utils.is_file_size_ok')
    def test_check_audio_file_success(self, mock_size_ok, mock_mime_ok, mock_ext_ok, mock_isfile):
        mock_isfile.return_value = True
        mock_ext_ok.return_value = True
        mock_mime_ok.return_value = True
        mock_size_ok.return_value = True
        self.assertTrue(audio_utils.check_audio_file("good_file.mp3"))

    @patch('os.path.isfile', return_value=False)
    def test_check_audio_file_raises_not_a_file(self, mock_isfile):
        with self.assertRaisesRegex(ValueError, "File does not exist: not_a_file.mp3"):
            audio_utils.check_audio_file("not_a_file.mp3")

    @patch('os.path.isfile', return_value=True)
    @patch('audio_input.utils.is_allowed_audio_file', return_value=False)
    @patch('audio_input.utils.ALLOWED_EXTENSIONS', {'.mp3', '.wav'}) # For error message
    def test_check_audio_file_raises_bad_extension(self, mock_ext_ok, mock_isfile):
        with self.assertRaisesRegex(ValueError, "Unsupported file type: bad_ext.txt. Allowed types: .mp3, .wav"):
            audio_utils.check_audio_file("bad_ext.txt")

    @patch('os.path.isfile', return_value=True)
    @patch('audio_input.utils.is_allowed_audio_file', return_value=True)
    @patch('audio_input.utils.is_valid_audio_mime', return_value=False)
    def test_check_audio_file_raises_bad_mime(self, mock_mime_ok, mock_ext_ok, mock_isfile):
        with self.assertRaisesRegex(ValueError, "Invalid audio MIME type for file: bad_mime.mp3"):
            audio_utils.check_audio_file("bad_mime.mp3")

    @patch('os.path.isfile', return_value=True)
    @patch('audio_input.utils.is_allowed_audio_file', return_value=True)
    @patch('audio_input.utils.is_valid_audio_mime', return_value=True)
    @patch('audio_input.utils.is_file_size_ok', return_value=False)
    @patch('audio_input.utils.MAX_FILE_SIZE_MB', 5) # For error message
    def test_check_audio_file_raises_too_large(self, mock_size_ok, mock_mime_ok, mock_ext_ok, mock_isfile):
        with self.assertRaisesRegex(ValueError, "File too large \(>5 MB\): too_large.mp3"):
            audio_utils.check_audio_file("too_large.mp3")

if __name__ == '__main__':
    unittest.main()
