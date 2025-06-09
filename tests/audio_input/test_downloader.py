import unittest
from unittest.mock import patch, MagicMock
import os
import sys

from audio_input.downloader import download_audio

# Store original import for use in mock side effects
original_builtins_import = __import__

class MockYTDLPUtils: # For mocking yt_dlp.utils.DownloadError
    class DownloadError(Exception):
        pass

class TestDownloadAudio(unittest.TestCase):

    def setUp(self):
        self.mock_yt_dlp_utils_module = MockYTDLPUtils()
        # Patch sys.modules to provide our mock DownloadError via a mock utils module
        self.patcher_sys_modules_yt_dlp_utils = patch.dict(
            sys.modules, 
            {'yt_dlp.utils': self.mock_yt_dlp_utils_module}
        )
        self.patcher_sys_modules_yt_dlp_utils.start()

    def tearDown(self):
        self.patcher_sys_modules_yt_dlp_utils.stop()

    @patch('shutil.which')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_download_success_filepath_from_requested_downloads(self, mock_path_exists, mock_makedirs, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/path/to/ffmpeg"
        mock_path_exists.return_value = True

        mock_yt_dlp_module = MagicMock(name="mock_yt_dlp_module")
        MockYoutubeDL_class = MagicMock(name="MockYoutubeDL_class")
        mock_yt_dlp_module.YoutubeDL = MockYoutubeDL_class
        mock_ydl_instance = MockYoutubeDL_class.return_value.__enter__.return_value
        
        expected_filepath = os.path.join("test_out", "Test Title.mp3")
        mock_info_dict = {
            'title': 'Test Title', 'ext': 'mp3',
            'requested_downloads': [{'filepath': expected_filepath}]
        }
        mock_ydl_instance.extract_info.return_value = mock_info_dict

        def import_side_effect(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_builtins_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_side_effect):
            result_path = download_audio("fake_url", out_dir="test_out")

        self.assertEqual(result_path, expected_filepath)
        MockYoutubeDL_class.assert_called_once()
        mock_ydl_instance.extract_info.assert_called_once_with("fake_url", download=True)

    @patch('shutil.which')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_download_success_filepath_from_info_dict(self, mock_path_exists, mock_makedirs, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/ffmpeg"
        mock_path_exists.return_value = True

        mock_yt_dlp_module = MagicMock(name="mock_yt_dlp_module_info")
        MockYoutubeDL_class = MagicMock(name="MockYoutubeDL_class_info")
        mock_yt_dlp_module.YoutubeDL = MockYoutubeDL_class
        mock_ydl_instance = MockYoutubeDL_class.return_value.__enter__.return_value
        
        expected_filepath = os.path.join("test_out", "Another Title.mp3")
        mock_info_dict = {'title': 'Another Title', 'ext': 'mp3', 'filepath': expected_filepath}
        mock_ydl_instance.extract_info.return_value = mock_info_dict

        def import_side_effect_info(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_builtins_import(name, *args, **kwargs)

        # Simulate the final file existing
        # The lambda for side_effect needs to capture the current mock_path_exists
        current_mock_path_exists = mock_path_exists 
        with patch('builtins.__import__', side_effect=import_side_effect_info), \
             patch('os.path.exists', MagicMock(side_effect=lambda p: p == expected_filepath or current_mock_path_exists(p))):
            result_path = download_audio("fake_url2", out_dir="test_out")
            self.assertEqual(result_path, expected_filepath)

    @patch('shutil.which')
    def test_yt_dlp_not_installed(self, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/ffmpeg"
        
        def import_side_effect_fail(name, *args, **kwargs):
            if name == 'yt_dlp': raise ImportError("yt-dlp is not installed")
            return original_builtins_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_side_effect_fail), \
             self.assertRaisesRegex(ImportError, "yt-dlp is required"):
            download_audio("fake_url")

    @patch('shutil.which')
    def test_ffmpeg_not_found(self, mock_shutil_which):
        mock_shutil_which.return_value = None # ffmpeg is NOT found
        # yt_dlp import should succeed for this test
        mock_yt_dlp_module = MagicMock()
        def import_side_effect_ffmpeg(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_builtins_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_side_effect_ffmpeg), \
             self.assertRaisesRegex(FileNotFoundError, "ffmpeg not found in PATH"):
            download_audio("fake_url")

    @patch('shutil.which')
    def test_download_fails_download_error(self, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/ffmpeg"
        
        mock_yt_dlp_module = MagicMock(name="mock_yt_dlp_module_dl_err")
        MockYoutubeDL_class = MagicMock(name="MockYoutubeDL_class_dl_err")
        mock_yt_dlp_module.YoutubeDL = MockYoutubeDL_class
        # Ensure the mocked yt_dlp module has a 'utils' attribute pointing to our mock utils
        mock_yt_dlp_module.utils = self.mock_yt_dlp_utils_module
        mock_ydl_instance = MockYoutubeDL_class.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = self.mock_yt_dlp_utils_module.DownloadError("Network issue")
        
        def import_side_effect_dl(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_builtins_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_side_effect_dl), \
             self.assertRaisesRegex(Exception, "Audio download failed \(yt-dlp error\): Network issue"):
            download_audio("fake_url")

    @patch('shutil.which')
    def test_download_fails_generic_exception_in_yt_dlp(self, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/ffmpeg"

        mock_yt_dlp_module = MagicMock(name="mock_yt_dlp_module_gen_err")
        MockYoutubeDL_class = MagicMock(name="MockYoutubeDL_class_gen_err")
        mock_yt_dlp_module.YoutubeDL = MockYoutubeDL_class
        # Ensure the mocked yt_dlp module has a 'utils' attribute for consistency, though not strictly needed for generic Exception
        mock_yt_dlp_module.utils = self.mock_yt_dlp_utils_module 
        mock_ydl_instance = MockYoutubeDL_class.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = Exception("Some other yt-dlp problem")

        def import_side_effect_gen(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_builtins_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=import_side_effect_gen), \
             self.assertRaisesRegex(Exception, "Audio download processing failed: Some other yt-dlp problem"):
            download_audio("fake_url")
            
    @patch('shutil.which')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_output_directory_creation(self, mock_makedirs, mock_path_exists, mock_shutil_which):
        mock_shutil_which.return_value = "/fake/ffmpeg"
        mock_path_exists.side_effect = [False, True, True] 

        mock_yt_dlp_module = MagicMock(name="mock_yt_dlp_module_mkdir")
        MockYoutubeDL_class = MagicMock(name="MockYoutubeDL_class_mkdir")
        mock_yt_dlp_module.YoutubeDL = MockYoutubeDL_class
        mock_ydl_instance = MockYoutubeDL_class.return_value.__enter__.return_value
        
        expected_filepath = os.path.join("new_dir", "Test.mp3")
        mock_info_dict = {'requested_downloads': [{'filepath': expected_filepath}], 'title': 'Test', 'ext': 'mp3'}
        mock_ydl_instance.extract_info.return_value = mock_info_dict
        
        original_import = __import__
        def import_side_effect_mkdir(name, *args, **kwargs):
            if name == 'yt_dlp': return mock_yt_dlp_module
            return original_import(name, *args, **kwargs)

        # Simulate the final file existing after download
        # This needs to be careful not to interfere with the mock_path_exists for directory creation
        # original_os_path_exists = os.path.exists # Unused variable
        def complex_path_exists_side_effect(path_arg):
            if path_arg == "new_dir": # First call for directory
                return False # Directory doesn't exist
            if path_arg == expected_filepath: # Call for file
                return True # File exists
            return True # Other general checks for directory existence after creation

        # We need to control os.path.exists for both directory and file checks.
        # The mock_path_exists is already patched for the test method.
        # Let's refine its side_effect.
        
        # mock_path_exists is for the directory. We need another for the file.
        # The current mock_path_exists.side_effect = [False, True, True] handles:
        # 1. Initial check for out_dir (False)
        # 2. Check after makedirs (True) - this might not be explicitly checked by downloader
        # 3. Check for final_filepath (True)
        
        # Let's make the side_effect more explicit for the file check within the download logic
        # The downloader's os.path.exists(final_filepath) needs to be True.
        
        # The current mock_path_exists.side_effect should be [False, True] for directory,
        # then the file existence check is separate.
        mock_path_exists.side_effect = [False, True] # For directory check

        with patch('builtins.__import__', side_effect=import_side_effect_mkdir), \
             patch('os.path.exists', side_effect=lambda p: True if p == expected_filepath else mock_path_exists(p) if p == "new_dir" else True):
            # The lambda ensures that if path is expected_filepath, it's True.
            # If path is "new_dir", it uses the mock_path_exists behavior.
            # Otherwise, defaults to True (e.g. for the out_dir check after makedirs if any)
            download_audio("fake_url", out_dir="new_dir")

        mock_makedirs.assert_called_once_with("new_dir")

if __name__ == '__main__':
    unittest.main()
