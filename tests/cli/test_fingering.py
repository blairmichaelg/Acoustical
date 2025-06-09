import unittest
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from cli.commands.fingering import fingering_command
from music_theory.chord_shapes import ChordShape 
from music_theory.fretboard import Fretboard # Import Fretboard to patch it

class TestFingeringCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.fingering.suggest_fingerings')
    def test_fingering_suggestion_success(self, mock_suggest_fingerings):
        # Create mock ChordShape objects
        mock_shape1 = MagicMock(spec=ChordShape)
        mock_shape1.name = "C Major Shape 1"
        mock_shape1.template_root_note_str = "C"
        mock_shape1.chord_type = "maj"
        mock_shape1.base_fret_of_template = 0
        mock_shape1.fingerings = [[0, 3, 1], [1, 2, 2], [2, 0, 0], [3, 1, 1], [4, 0, 0], [5, 0, 0]] # Use lists for comparison
        mock_shape1.is_movable = False
        mock_shape1.barre_strings_offset = None

        mock_shape2 = MagicMock(spec=ChordShape)
        mock_shape2.name = "C Major Shape 2"
        mock_shape2.template_root_note_str = "C"
        mock_shape2.chord_type = "maj"
        mock_shape2.base_fret_of_template = 3
        mock_shape2.fingerings = [[0, 3, 1], [1, 5, 3], [2, 5, 4], [3, 5, 2], [4, 3, 1], [5, 3, 1]] # Use lists for comparison
        mock_shape2.is_movable = True
        mock_shape2.barre_strings_offset = (0, 4) # Example barre

        mock_suggest_fingerings.return_value = [
            (mock_shape1, 10), # shape, score
            (mock_shape2, 20)
        ]

        chord_string = "C"
        num_suggestions = 2

        result = self.runner.invoke(fingering_command, [chord_string, '--num_suggestions', str(num_suggestions)])

        self.assertEqual(result.exit_code, 0)
        mock_suggest_fingerings.assert_called_once_with(chord_string, fretboard=unittest.mock.ANY)
        
        output_json = json.loads(result.output)
        self.assertEqual(output_json["chord"], chord_string)
        self.assertEqual(len(output_json["suggestions"]), num_suggestions)

        expected_names = {"C Major Shape 1", "C Major Shape 2"}
        actual_names = {s["name"] for s in output_json["suggestions"]}
        self.assertEqual(actual_names, expected_names)

        expected_scores = {10, 20}
        actual_scores = {s["score"] for s in output_json["suggestions"]}
        self.assertEqual(actual_scores, expected_scores)

        for s in output_json["suggestions"]:
            if s["name"] == "C Major Shape 1":
                self.assertEqual(s["root"], "C")
                self.assertEqual(s["type"], "maj")
                self.assertEqual(s["base_fret"], 0)
                self.assertEqual(s["fingerings"], [[0, 3, 1], [1, 2, 2], [2, 0, 0], [3, 1, 1], [4, 0, 0], [5, 0, 0]])
                self.assertEqual(s["is_movable"], False)
                self.assertEqual(s["barre_strings"], None)
            elif s["name"] == "C Major Shape 2":
                self.assertEqual(s["root"], "C")
                self.assertEqual(s["type"], "maj")
                self.assertEqual(s["base_fret"], 3)
                self.assertEqual(s["fingerings"], [[0, 3, 1], [1, 5, 3], [2, 5, 4], [3, 5, 2], [4, 3, 1], [5, 3, 1]])
                self.assertEqual(s["is_movable"], True)
                self.assertEqual(s["barre_strings"], [0, 4]) # Barre strings are list in JSON

    @patch('cli.commands.fingering.suggest_fingerings')
    def test_fingering_no_suggestions_found(self, mock_suggest_fingerings):
        mock_suggest_fingerings.return_value = []
        chord_string = "InvalidChord"
        result = self.runner.invoke(fingering_command, [chord_string])
        self.assertEqual(result.exit_code, 0) 
        self.assertIn(f"No fingerings found for '{chord_string}'.", result.output)
        self.assertIn("Try a more common chord or check spelling.", result.output)

    @patch('cli.commands.fingering.suggest_fingerings')
    def test_fingering_general_exception(self, mock_suggest_fingerings):
        mock_suggest_fingerings.side_effect = Exception("Internal error")
        chord_string = "C"
        result = self.runner.invoke(fingering_command, [chord_string])
        self.assertEqual(result.exit_code, 1)
        self.assertIn(f"Failed to suggest fingerings for '{chord_string}'.", result.output)
        self.assertIn("Internal error", result.output)

    @patch('cli.commands.fingering.suggest_fingerings')
    @patch('cli.commands.fingering.Fretboard') # Patch Fretboard constructor
    def test_fingering_custom_tuning(self, MockFretboard, mock_suggest_fingerings):
        mock_suggest_fingerings.return_value = [] 
        chord_string = "C"
        tuning_str = "D,A,D,G,B,e" # Comma-separated tuning string
        
        result = self.runner.invoke(fingering_command, [chord_string, '--tuning', tuning_str])
        
        self.assertEqual(result.exit_code, 0)
        MockFretboard.assert_called_once_with(tuning=["D", "A", "D", "G", "B", "e"])
        mock_suggest_fingerings.assert_called_once_with(chord_string, fretboard=MockFretboard.return_value)

if __name__ == '__main__':
    unittest.main()
