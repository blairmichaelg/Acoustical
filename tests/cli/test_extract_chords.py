import unittest
import os
import json
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.extract_chords import extract_chords

class TestExtractChordsCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.extract_chords.get_chords')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_local_file_success(self, mock_check_audio_file, mock_get_chords):
        mock_get_chords.return_value = [{"time": 0.0, "chord": "C"}]
        
        with self.runner.isolated_filesystem():
            # Create a dummy audio file
            with open('test_audio.mp3', 'w') as f:
                f.write("dummy audio content")
            
            result = self.runner.invoke(extract_chords, ['test_audio.mp3'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), [{"time": 0.0, "chord": "C"}])
            mock_check_audio_file.assert_called_once_with('test_audio.mp3')
            mock_get_chords.assert_called_once_with('test_audio.mp3')

    @patch('cli.commands.extract_chords.get_chords')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_local_file_not_found(self, mock_check_audio_file, mock_get_chords):
        result = self.runner.invoke(extract_chords, ['non_existent.mp3'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Local audio file not found: non_existent.mp3", result.output)
        mock_check_audio_file.assert_not_called()
        mock_get_chords.assert_not_called()

    @patch('cli.commands.extract_chords.get_chords')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_url_success(self, mock_check_audio_file, mock_get_chords):
        mock_get_chords.return_value = [{"time": 0.0, "chord": "G"}]
        url = "http://example.com/song.mp3"
        
        result = self.runner.invoke(extract_chords, [url])
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output), [{"time": 0.0, "chord": "G"}])
        mock_check_audio_file.assert_not_called() # check_audio_file is skipped for URLs
        mock_get_chords.assert_called_once_with(url)

    @patch('cli.commands.extract_chords.get_chords_batch')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_batch_success(self, mock_check_audio_file, mock_get_chords_batch):
        # The mock should return paths as they would be passed to it by the CLI command
        mock_get_chords_batch.return_value = {
            os.path.join('test_dir', "audio1.mp3"): [{"time": 0.0, "chord": "C"}],
            os.path.join('test_dir', "audio2.wav"): [{"time": 0.0, "chord": "G"}]
        }
        
        with self.runner.isolated_filesystem():
            os.makedirs('test_dir')
            with open('test_dir/audio1.mp3', 'w') as f: f.write("dummy")
            with open('test_dir/audio2.wav', 'w') as f: f.write("dummy")
            with open('test_dir/not_audio.txt', 'w') as f: f.write("dummy") # Should be skipped
            
            result = self.runner.invoke(extract_chords, ['test_dir', '--batch'])
            
            self.assertEqual(result.exit_code, 0)
            # Normalize paths in the expected output for OS compatibility
            expected_output_dict = {
                os.path.normpath(os.path.join('test_dir', "audio1.mp3")): [{"time": 0.0, "chord": "C"}],
                os.path.normpath(os.path.join('test_dir', "audio2.wav")): [{"time": 0.0, "chord": "G"}]
            }
            self.assertEqual(json.loads(result.output), expected_output_dict)
            # check_audio_file should be called for each valid audio file
            mock_check_audio_file.assert_any_call(os.path.join('test_dir', 'audio1.mp3'))
            mock_check_audio_file.assert_any_call(os.path.join('test_dir', 'audio2.wav'))
            self.assertEqual(mock_check_audio_file.call_count, 2)
            mock_get_chords_batch.assert_called_once()
            # Verify arguments passed to get_chords_batch (order might vary)
            args, _ = mock_get_chords_batch.call_args
            self.assertIsInstance(args[0], list)
            self.assertIn(os.path.join('test_dir', 'audio1.mp3'), args[0])
            self.assertIn(os.path.join('test_dir', 'audio2.wav'), args[0])
            self.assertEqual(len(args[0]), 2)


    @patch('cli.commands.extract_chords.get_chords_batch')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_batch_source_not_directory(self, mock_check_audio_file, mock_get_chords_batch):
        with self.runner.isolated_filesystem():
            with open('test_file.mp3', 'w') as f: f.write("dummy")
            
            result = self.runner.invoke(extract_chords, ['test_file.mp3', '--batch'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Batch mode requires a local directory path, but 'test_file.mp3' is not a directory.", result.output)
            mock_check_audio_file.assert_not_called()
            mock_get_chords_batch.assert_not_called()

    @patch('cli.commands.extract_chords.get_chords_batch')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_batch_no_valid_audio_files(self, mock_check_audio_file, mock_get_chords_batch):
        with self.runner.isolated_filesystem():
            os.makedirs('empty_dir')
            with open('empty_dir/not_audio.txt', 'w') as f: f.write("dummy")
            
            result = self.runner.invoke(extract_chords, ['empty_dir', '--batch'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("No valid audio files found in batch directory.", result.output)
            mock_check_audio_file.assert_not_called() # check_audio_file is not called if files are filtered by extension
            mock_get_chords_batch.assert_not_called()

    @patch('cli.commands.extract_chords.get_chords')
    @patch('cli.commands.extract_chords.check_audio_file')
    def test_extract_chords_general_exception(self, mock_check_audio_file, mock_get_chords):
        mock_get_chords.side_effect = Exception("General extraction error")
        
        with self.runner.isolated_filesystem():
            with open('test_audio.mp3', 'w') as f:
                f.write("dummy audio content")
            
            result = self.runner.invoke(extract_chords, ['test_audio.mp3'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Chord extraction failed: General extraction error", result.output)
            self.assertIn("Tip: Run 'python cli/cli.py check-backends' to diagnose backend availability or check your URL/file path.", result.output)

if __name__ == '__main__':
    unittest.main()
