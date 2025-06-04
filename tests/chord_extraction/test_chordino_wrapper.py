import unittest
from unittest.mock import patch, MagicMock
import platform

from chord_extraction.chordino_wrapper import ChordinoBackend, register_backend
from chord_extraction.backend_registry import unregister_backend_by_method

# Store original platform.system to restore after tests
original_platform_system = platform.system

class TestChordinoBackend(unittest.TestCase):

    def tearDown(self):
        unregister_backend_by_method(ChordinoBackend.extract_chords)
        # Restore platform.system if it was mocked for a specific test
        platform.system = original_platform_system

    def test_is_available_vamp_present_non_windows(self):
        with patch('platform.system', return_value="Linux"), \
             patch('builtins.__import__', MagicMock(return_value=MagicMock())) as mock_import:
            # Ensure 'vamp' import is successful within the context of is_available
            # The actual 'vamp' module is mocked by MagicMock for the import check
            self.assertTrue(ChordinoBackend.is_available())
            # Check if 'vamp' was attempted to be imported
            called_with_vamp = any(call_args[0][0] == 'vamp' for call_args in mock_import.call_args_list)
            self.assertTrue(called_with_vamp, "import vamp was not called")


    def test_is_available_vamp_present_windows(self):
        with patch('platform.system', return_value="Windows"), \
             patch('builtins.__import__', MagicMock(return_value=MagicMock())): # Removed 'as mock_import'
            self.assertFalse(ChordinoBackend.is_available())
            # Vamp import is still attempted by the code, but the platform check causes it to return False.

    def test_is_available_vamp_absent(self):
        with patch('platform.system', return_value="Linux"), \
             patch('builtins.__import__', side_effect=ImportError("No module named vamp")) as mock_import:
            self.assertFalse(ChordinoBackend.is_available())
            called_with_vamp = any(call_args[0][0] == 'vamp' for call_args in mock_import.call_args_list)
            self.assertTrue(called_with_vamp, "import vamp was not called")

    def test_extract_chords_not_available_due_to_platform(self):
        with patch('platform.system', return_value="Windows"), \
             patch('builtins.__import__', MagicMock(return_value=MagicMock())): # vamp import succeeds
            # is_available will return False due to Windows
            with self.assertRaisesRegex(NotImplementedError, "Chordino is not supported"):
                ChordinoBackend.extract_chords("dummy.wav")

    def test_extract_chords_not_available_due_to_vamp_missing(self):
        with patch('platform.system', return_value="Linux"), \
             patch('builtins.__import__', side_effect=ImportError("No module named vamp")):
            # is_available will return False due to ImportError
            with self.assertRaisesRegex(NotImplementedError, "Chordino is not supported"):
                ChordinoBackend.extract_chords("dummy.wav")
    
    def test_extract_chords_stub_implementation_runs_when_available(self):
        # This test assumes the STUB implementation is active and we are on a non-Windows platform
        # where vamp is supposedly available.
        with patch('platform.system', return_value="Linux"), \
             patch('builtins.__import__', MagicMock(return_value=MagicMock())) as mock_vamp_import:
            
            register_backend(ChordinoBackend) # Ensure registered

            # Since the actual implementation is a stub, we just check if it returns the stubbed data
            expected_stub_data = [{"time": 0.0, "chord": "C (stub)"}, {"time": 2.0, "chord": "G (stub)"}]
            result = ChordinoBackend.extract_chords("dummy.wav")
            self.assertEqual(result, expected_stub_data)
            called_with_vamp = any(call_args[0][0] == 'vamp' for call_args in mock_vamp_import.call_args_list)
            self.assertTrue(called_with_vamp, "import vamp was not called")


if __name__ == '__main__':
    unittest.main()
