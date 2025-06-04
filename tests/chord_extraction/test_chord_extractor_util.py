import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json

from chord_extraction.chord_extractor_util import ChordExtractorBackend, register_backend
from chord_extraction.backend_registry import unregister_backend_by_method

class TestChordExtractorBackend(unittest.TestCase):

    def tearDown(self):
        unregister_backend_by_method(ChordExtractorBackend.extract_chords)

    @patch('shutil.which')
    def test_is_available_when_cli_present(self, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor" # Dummy path
        self.assertTrue(ChordExtractorBackend.is_available())
        mock_shutil_which.assert_called_once_with('chord-extractor')

    @patch('shutil.which')
    def test_is_available_when_cli_absent(self, mock_shutil_which):
        mock_shutil_which.return_value = None
        self.assertFalse(ChordExtractorBackend.is_available())

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_success(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        
        mock_completed_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_completed_process.stdout = json.dumps([{"time": 0.0, "chord": "C"}, {"time": 1.0, "chord": "G"}])
        mock_completed_process.stderr = ""
        mock_completed_process.returncode = 0
        # mock_completed_process.check_returncode.return_value = None # Not needed if check=True
        mock_subprocess_run.return_value = mock_completed_process
        
        register_backend(ChordExtractorBackend) # Ensure it's registered for the call

        expected_output = [{"time": 0.0, "chord": "C"}, {"time": 1.0, "chord": "G"}]
        result = ChordExtractorBackend.extract_chords("dummy.wav")
        
        self.assertEqual(result, expected_output)
        mock_subprocess_run.assert_called_once_with(
            ["chord-extractor", "--input", "dummy.wav", "--output-format", "json"],
            capture_output=True, text=True, check=True, timeout=120
        )

    @patch('shutil.which')
    def test_extract_chords_cli_not_available(self, mock_shutil_which):
        mock_shutil_which.return_value = None
        with self.assertRaisesRegex(RuntimeError, "chord-extractor CLI is not installed or not in PATH."):
            ChordExtractorBackend.extract_chords("dummy.wav")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_subprocess_called_process_error(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="chord-extractor", stderr="Some error"
        )
        register_backend(ChordExtractorBackend)
        with self.assertRaisesRegex(RuntimeError, "chord-extractor CLI failed"):
            ChordExtractorBackend.extract_chords("dummy.wav")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_timeout(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="chord-extractor", timeout=120)
        register_backend(ChordExtractorBackend)
        with self.assertRaisesRegex(RuntimeError, "chord-extractor backend timed out"):
            ChordExtractorBackend.extract_chords("dummy.wav")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_invalid_json_output(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        mock_completed_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_completed_process.stdout = "this is not json"
        mock_subprocess_run.return_value = mock_completed_process
        register_backend(ChordExtractorBackend)
        with self.assertRaisesRegex(RuntimeError, "chord-extractor returned invalid JSON"):
            ChordExtractorBackend.extract_chords("dummy.wav")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_incorrect_json_structure(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        mock_completed_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_completed_process.stdout = json.dumps({"wrong": "structure"}) # Not a list
        mock_subprocess_run.return_value = mock_completed_process
        register_backend(ChordExtractorBackend)
        with self.assertRaisesRegex(ValueError, "Invalid output format from chord-extractor"):
            ChordExtractorBackend.extract_chords("dummy.wav")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_extract_chords_incorrect_json_item_structure(self, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = "/usr/bin/chord-extractor"
        mock_completed_process = MagicMock(spec=subprocess.CompletedProcess)
        # List, but item is not a dict or missing keys
        mock_completed_process.stdout = json.dumps([{"note": "C", "start": 0.0}]) 
        mock_subprocess_run.return_value = mock_completed_process
        register_backend(ChordExtractorBackend)
        with self.assertRaisesRegex(ValueError, "Invalid output format from chord-extractor"):
            ChordExtractorBackend.extract_chords("dummy.wav")


if __name__ == '__main__':
    unittest.main()
