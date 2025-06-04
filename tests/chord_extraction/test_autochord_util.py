import unittest
from unittest.mock import patch, MagicMock
# import logging # Unused import

# Temporarily adjust autochord_util path if tests are run from root or specific test dir
# This might be needed if the test runner doesn't handle package paths correctly by default.
# For `python -m unittest tests.chord_extraction.test_autochord_util`, it should be fine.
from chord_extraction.autochord_util import AutochordBackend, register_backend
# Unregister to avoid side effects if tests are run multiple times or in a suite
from chord_extraction.backend_registry import unregister_backend_by_method # Removed get_registered_plugins

class TestAutochordBackend(unittest.TestCase):

    def tearDown(self):
        # Ensure AutochordBackend.extract_chords is removed from the registry after tests
        # This prevents interference between tests if the module is imported multiple times
        # or if other tests also register/unregister backends.
        unregister_backend_by_method(AutochordBackend.extract_chords)
        # As an extra precaution, ensure it's registered again if it was meant to be by default,
        # though typically each test run should start fresh or modules handle their own registration.
        # For now, just unregistering is sufficient for test isolation.

    def test_is_available_when_autochord_present(self):
        # autochord_util.guess_chords is patched to simulate it being importable
        with patch('chord_extraction.autochord_util.guess_chords', new_callable=MagicMock):
            self.assertTrue(AutochordBackend.is_available())

    def test_is_available_when_autochord_absent(self):
        # autochord_util.guess_chords is patched to None to simulate it NOT being importable
        with patch('chord_extraction.autochord_util.guess_chords', None):
            # The is_available method directly checks the module-level 'guess_chords' variable.
            # So, patching it directly affects the outcome of is_available().
            self.assertFalse(AutochordBackend.is_available())

    @patch('chord_extraction.autochord_util.guess_chords')
    def test_extract_chords_success(self, mock_guess_chords):
        # Ensure autochord is "available" for this test
        with patch('chord_extraction.autochord_util.AutochordBackend.is_available', return_value=True):
            mock_guess_chords.return_value = [(0.0, "C"), (1.5, "G"), (3.0, "Am")]
            expected_output = [{"time": 0.0, "chord": "C"}, {"time": 1.5, "chord": "G"}, {"time": 3.0, "chord": "Am"}]
            
            # Register the backend for this test if it's not already
            register_backend(AutochordBackend)
            
            result = AutochordBackend.extract_chords("dummy_path.wav")
            self.assertEqual(result, expected_output)
            mock_guess_chords.assert_called_once_with("dummy_path.wav")

    def test_extract_chords_not_available(self):
        with patch('chord_extraction.autochord_util.AutochordBackend.is_available', return_value=False):
            with self.assertRaisesRegex(ImportError, "autochord is not installed"):
                AutochordBackend.extract_chords("dummy_path.wav")

    @patch('chord_extraction.autochord_util.guess_chords')
    def test_extract_chords_extraction_fails(self, mock_guess_chords):
        with patch('chord_extraction.autochord_util.AutochordBackend.is_available', return_value=True):
            mock_guess_chords.side_effect = Exception("Test autochord failure")
            
            register_backend(AutochordBackend) # Ensure registered for the call

            with self.assertRaisesRegex(RuntimeError, "autochord extraction failed"):
                AutochordBackend.extract_chords("dummy_path.wav")

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG) # To see logs from the module
    unittest.main()
