import unittest
import json
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.capo import capo

class TestCapoCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.capo.recommend_capo')
    def test_capo_recommendation_success(self, mock_recommend_capo):
        # Mock the recommend_capo function to return a known value
        mock_recommend_capo.return_value = (3, ["D", "A", "Bm", "G"]) # Capo 3, C->D, G->A, Am->Bm, F->G

        # Prepare a dummy input JSON file content
        input_chords_content = json.dumps([
            {"chord": "C", "time": 0.0},
            {"chord": "G", "time": 1.0},
            {"chord": "Am", "time": 2.0},
            {"chord": "F", "time": 3.0}
        ])

        # Expected output JSON structure
        expected_output = {
            "capo": 3,
            "chords": [
                {"chord": "D", "time": 0.0},
                {"chord": "A", "time": 1.0},
                {"chord": "Bm", "time": 2.0},
                {"chord": "G", "time": 3.0}
            ]
        }

        # Invoke the command with the dummy input file
        with self.runner.isolated_filesystem():
            with open('input_chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(capo, ['input_chords.json'])

            # Assert the command ran successfully
            self.assertEqual(result.exit_code, 0)

            # Assert recommend_capo was called with the correct arguments
            mock_recommend_capo.assert_called_once_with(["C", "G", "Am", "F"])

            # Assert the output matches the expected JSON
            self.assertEqual(json.loads(result.output), expected_output)

    @patch('cli.commands.capo.recommend_capo')
    def test_capo_recommendation_empty_input(self, mock_recommend_capo):
        mock_recommend_capo.return_value = (0, []) # No capo, empty transposed list

        input_chords_content = json.dumps([])
        expected_output = {
            "capo": 0,
            "chords": []
        }

        with self.runner.isolated_filesystem():
            with open('empty_chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(capo, ['empty_chords.json'])

            self.assertEqual(result.exit_code, 0)
            mock_recommend_capo.assert_called_once_with([])
            self.assertEqual(json.loads(result.output), expected_output)

    def test_capo_recommendation_invalid_json(self):
        input_chords_content = "this is not valid json"

        with self.runner.isolated_filesystem():
            with open('invalid_chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(capo, ['invalid_chords.json'])

            # Assert the command failed with an error exit code
            self.assertEqual(result.exit_code, 1)
            # Assert the error message is as expected
            self.assertIn("Capo recommendation failed: Expecting value: line 1 column 1 (char 0)", result.output)

    @patch('cli.commands.capo.recommend_capo')
    def test_capo_recommendation_exception_from_advisor(self, mock_recommend_capo):
        mock_recommend_capo.side_effect = ValueError("Test error from recommend_capo")

        input_chords_content = json.dumps([{"chord": "C", "time": 0.0}])

        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(input_chords_content)
            
            result = self.runner.invoke(capo, ['chords.json'])

            self.assertEqual(result.exit_code, 1)
            self.assertIn("Capo recommendation failed: Test error from recommend_capo", result.output)

if __name__ == '__main__':
    unittest.main()
