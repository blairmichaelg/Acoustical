import unittest
import json
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.flourish import flourish

class TestFlourishCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.mock_chords_input = [
            {"chord": "C", "time": 0.0},
            {"chord": "G", "time": 1.0}
        ]
        self.mock_chords_json_content = json.dumps(self.mock_chords_input)

    @patch('cli.commands.flourish.apply_rule_based_flourishes')
    def test_flourish_rule_based_default(self, mock_apply_rule_based_flourishes):
        mock_apply_rule_based_flourishes.return_value = ["RuleBasedFlourish1", "RuleBasedFlourish2"]
        
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(self.mock_chords_json_content)
            
            result = self.runner.invoke(flourish, ['chords.json'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), {"flourishes": ["RuleBasedFlourish1", "RuleBasedFlourish2"]})
            mock_apply_rule_based_flourishes.assert_called_once_with(self.mock_chords_input)

    @patch('cli.commands.flourish.generate_magenta_flourish')
    def test_flourish_magenta_flag(self, mock_generate_magenta_flourish):
        mock_generate_magenta_flourish.return_value = ["MagentaFlourish1", "MagentaFlourish2"]
        
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(self.mock_chords_json_content)
            
            result = self.runner.invoke(flourish, ['chords.json', '--magenta'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), {"flourishes": ["MagentaFlourish1", "MagentaFlourish2"]})
            mock_generate_magenta_flourish.assert_called_once_with(["C", "G"]) # Magenta expects chord names only

    @patch('cli.commands.flourish.suggest_chord_substitutions')
    def test_flourish_gpt4all_flag(self, mock_suggest_chord_substitutions):
        mock_suggest_chord_substitutions.return_value = ["GPT4AllFlourish1", "GPT4AllFlourish2"]
        
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(self.mock_chords_json_content)
            
            result = self.runner.invoke(flourish, ['chords.json', '--gpt4all'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(json.loads(result.output), {"flourishes": ["GPT4AllFlourish1", "GPT4AllFlourish2"]})
            mock_suggest_chord_substitutions.assert_called_once_with(self.mock_chords_input) # GPT4All expects full chord objects

    def test_flourish_both_flags_error(self):
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(self.mock_chords_json_content)
            
            result = self.runner.invoke(flourish, ['chords.json', '--magenta', '--gpt4all'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Cannot use both --magenta and --gpt4all flags simultaneously. Please choose one.", result.output)

    def test_flourish_invalid_json(self):
        invalid_json_content = "this is not json"
        with self.runner.isolated_filesystem():
            with open('invalid_chords.json', 'w') as f:
                f.write(invalid_json_content)
            
            result = self.runner.invoke(flourish, ['invalid_chords.json'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Flourish suggestion failed: Expecting value: line 1 column 1 (char 0)", result.output)

    @patch('cli.commands.flourish.apply_rule_based_flourishes')
    def test_flourish_general_exception(self, mock_apply_rule_based_flourishes):
        mock_apply_rule_based_flourishes.side_effect = Exception("Internal flourish error")
        
        with self.runner.isolated_filesystem():
            with open('chords.json', 'w') as f:
                f.write(self.mock_chords_json_content)
            
            result = self.runner.invoke(flourish, ['chords.json'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn("Flourish suggestion failed: Internal flourish error", result.output)

if __name__ == '__main__':
    unittest.main()
