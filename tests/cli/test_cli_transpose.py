import unittest
import json
from unittest.mock import patch
from click.testing import CliRunner
from io import StringIO # Import StringIO

from cli.commands.transpose import transpose

class TestTransposeCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.transpose.transpose_chords')
    def test_transpose_success(self, mock_transpose_chords):
        mock_transpose_chords.return_value = ["D", "A", "Bm", "G"]
        
        input_chords_content = json.dumps([
            {"chord": "C", "time": 0.0},
            {"chord": "G", "time": 1.0},
            {"chord": "Am", "time": 2.0},
            {"chord": "F", "time": 3.0}
        ])
        expected_output = [
            {"chord": "D", "time": 0.0},
            {"chord": "A", "time": 1.0},
            {"chord": "Bm", "time": 2.0},
            {"chord": "G", "time": 3.0}
        ]

        # Pass '-' as the filename to indicate reading from stdin
        result = self.runner.invoke(transpose, ['-', '--semitones', '2'], input=input_chords_content)
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output.strip()), expected_output)
        mock_transpose_chords.assert_called_once_with(["C", "G", "Am", "F"], 2)

    @patch('cli.commands.transpose.transpose_chords')
    def test_transpose_empty_input(self, mock_transpose_chords):
        mock_transpose_chords.return_value = []
        
        input_chords_content = json.dumps([])
        expected_output = []

        # Pass '-' as the filename to indicate reading from stdin
        result = self.runner.invoke(transpose, ['-', '--semitones', '0'], input=input_chords_content)
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(json.loads(result.output.strip()), expected_output)
        mock_transpose_chords.assert_called_once_with([], 0)

    def test_transpose_invalid_json(self):
        invalid_json_content = "this is not json"
        # Pass '-' as the filename to indicate reading from stdin
        result = self.runner.invoke(transpose, ['-', '--semitones', '1'], input=invalid_json_content)
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Transposition failed: Expecting value: line 1 column 1 (char 0)", result.output)

    @patch('cli.commands.transpose.transpose_chords')
    def test_transpose_exception_from_advisor(self, mock_transpose_chords):
        mock_transpose_chords.side_effect = ValueError("Transposition logic error")
        
        input_chords_content = json.dumps([{"chord": "C", "time": 0.0}])
        # Pass '-' as the filename to indicate reading from stdin
        result = self.runner.invoke(transpose, ['-', '--semitones', '-1'], input=input_chords_content)
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Transposition failed: Transposition logic error", result.output)

    def test_transpose_missing_semitones(self):
        input_chords_content = json.dumps([{"chord": "C", "time": 0.0}])
        # Pass '-' as the filename to indicate reading from stdin
        result = self.runner.invoke(transpose, ['-'], input=input_chords_content) # Pass '-' for chords_json
        
        self.assertEqual(result.exit_code, 2) # Click's default for missing required option
        self.assertIn("Error: Missing option '--semitones'", result.output)

if __name__ == '__main__':
    unittest.main()
