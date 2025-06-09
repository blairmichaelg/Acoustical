import unittest
import json
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.key import key

class TestKeyCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.key.detect_key_from_chords')
    def test_key_detection_success(self, mock_detect_key_from_chords):
        mock_detect_key_from_chords.return_value = {"key_root": "C", "key_quality": "major"}
        
        input_chords_content = json.dumps([
            {"chord": "C", "time": 0.0},
            {"chord": "G", "time": 1.0},
            {"chord": "Am", "time": 2.0}
        ])
        expected_output = {"key": {"key_root": "C", "key_quality": "major"}}

        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(key, ['chords.json'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), expected_output)
            mock_detect_key_from_chords.assert_called_once_with(["C", "G", "Am"])

    @patch('cli.commands.key.detect_key_from_chords')
    def test_key_detection_empty_input(self, mock_detect_key_from_chords):
        mock_detect_key_from_chords.return_value = {"key_root": None, "key_quality": None}
        
        input_chords_content = json.dumps([])
        expected_output = {"key": {"key_root": None, "key_quality": None}}

        with self.runner.isolated_filesystem():
            with open('empty_chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(key, ['empty_chords.json'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), expected_output)
            mock_detect_key_from_chords.assert_called_once_with([])

    def test_key_detection_invalid_json(self):
        invalid_json_content = "this is not json"
        with self.runner.isolated_filesystem():
            with open('invalid_chords.json', 'w') as f:
                f.write(invalid_json_content)
            
            result = self.runner.invoke(key, ['invalid_chords.json'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Key detection failed: Expecting value: line 1 column 1 (char 0)", result.output)

    @patch('cli.commands.key.detect_key_from_chords')
    def test_key_detection_exception_from_advisor(self, mock_detect_key_from_chords):
        mock_detect_key_from_chords.side_effect = ValueError("Key analysis error")
        
        input_chords_content = json.dumps([{"chord": "C", "time": 0.0}])
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(key, ['chords.json'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Key detection failed: Key analysis error", result.output)

if __name__ == '__main__':
    unittest.main()
