import unittest
from unittest.mock import patch 
import logging # Added for log capture

# music_theory_utils not directly used in these tests, functions are called via rule_based

# Assuming rule_based.py is in flourish_engine directory
from flourish_engine import rule_based

# Mock config directly for simplicity in tests
MOCK_CONFIG_SUBSTITUTIONS = {
    "default": {
        "simple_substitutions": {
            "C": "Cadd9",
            "G": "G7" 
        }
        # Add other rule types if the function evolves to use them from config
    },
    "empty_set": {},
    "custom_set": {
        "simple_substitutions": {
            "Am": "Am7sus4"
        }
    }
}

class TestRuleBasedFlourishes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure logging to see debug messages from the module during tests
        # This will apply to all tests in this class
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
        # If you want to capture logs per test, use self.assertLogs in each test method

    def _assert_suggestions_contain(self, flourish_results, original_chord, expected_suggestion):
        found_original = False
        for item in flourish_results:
            if item["original_chord"] == original_chord:
                found_original = True
                self.assertIn(expected_suggestion, item["suggestions"], 
                              f"Expected '{expected_suggestion}' for '{original_chord}', got {item['suggestions']}")
                break
        self.assertTrue(found_original, f"Original chord '{original_chord}' not found in results.")

    def _get_suggestions_for_chord(self, flourish_results, original_chord_str):
        for item in flourish_results:
            if item["original_chord"] == original_chord_str:
                return item["suggestions"]
        return None

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_no_key_detected_uses_sus_and_config(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {} # No key detected
        progression = [{"chord": "C", "time": 0.0}, {"chord": "D", "time": 1.0}]
        
        results = rule_based.apply_rule_based_flourishes(progression, "default")
        
        # For C (in default config: C -> Cadd9)
        c_suggestions = self._get_suggestions_for_chord(results, "C")
        self.assertIsNotNone(c_suggestions)
        self.assertIn("C", c_suggestions)
        self.assertIn("Cadd9", c_suggestions) # From config
        self.assertIn("Csus2", c_suggestions) # Default rule
        self.assertIn("Csus4", c_suggestions) # Default rule
        self.assertIn("C#dim", c_suggestions) # Passing to D

        # For D (not in config)
        d_suggestions = self._get_suggestions_for_chord(results, "D")
        self.assertIsNotNone(d_suggestions)
        self.assertIn("D", d_suggestions)
        self.assertIn("Dsus2", d_suggestions)
        self.assertIn("Dsus4", d_suggestions)

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_simple_substitutions_from_custom_config(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {} # No key
        progression = [{"chord": "Am", "time": 0.0}]
        results = rule_based.apply_rule_based_flourishes(progression, "custom_set")
        
        am_suggestions = self._get_suggestions_for_chord(results, "Am")
        self.assertIn("Am7sus4", am_suggestions) # From custom_set config

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_diatonic_7ths_major_key(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {"key_root": "C", "key_quality": "major"}
        progression = [
            {"chord": "C", "time": 0.0},  # I in C major -> Cmaj7
            {"chord": "Dm", "time": 1.0}, # ii in C major -> Dm7
            {"chord": "G", "time": 2.0}   # V in C major -> G7
        ]
        results = rule_based.apply_rule_based_flourishes(progression, "default")

        self._assert_suggestions_contain(results, "C", "Cmaj7")
        self._assert_suggestions_contain(results, "Dm", "Dm7")
        self.assertIn("G7", self._get_suggestions_for_chord(results, "G")) # G7 from config and also diatonic dominant

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_diatonic_7ths_minor_key(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {"key_root": "A", "key_quality": "minor"} # A natural minor
        progression = [
            {"chord": "Am", "time": 0.0}, # i in A minor -> Am7
            {"chord": "C", "time": 1.0},  # III in A minor -> Cmaj7
            {"chord": "E", "time": 2.0}   # V in A harmonic/melodic minor -> E7 (G# is leading tone)
                                          # In natural minor, E is Em, G is diatonic. E7 needs G#.
                                          # The current key_scale_notes is for natural minor.
                                          # So E7 might not be suggested if G# is not in A natural minor scale.
                                          # Let's check the logic: E (E-G#-B). m7 is D. M7 is D#.
                                          # For E to become E7 (E-G#-B-D), D must be diatonic. D is in A natural minor.
                                          # So, E7 should be suggested.
        ]
        results = rule_based.apply_rule_based_flourishes(progression, "default")
        self._assert_suggestions_contain(results, "Am", "Am7")
        self._assert_suggestions_contain(results, "C", "Cmaj7") # C-E-G, B is M7, B is in A natural minor.
        self._assert_suggestions_contain(results, "E", "E7")   # E-G#-B, D is m7, D is in A natural minor.

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_sus_chords(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {} # No key, sus chords are not key-dependent by current rule
        progression = [{"chord": "C", "time": 0.0}, {"chord": "Am", "time": 1.0}]
        results = rule_based.apply_rule_based_flourishes(progression, "default")
        
        self._assert_suggestions_contain(results, "C", "Csus2")
        self._assert_suggestions_contain(results, "C", "Csus4")
        self._assert_suggestions_contain(results, "Am", "Amsus2")
        self._assert_suggestions_contain(results, "Am", "Amsus4")

        prog_no_sus = [{"chord": "Csus4", "time": 0.0}, {"chord": "Adim", "time": 1.0}]
        results_no_sus = rule_based.apply_rule_based_flourishes(prog_no_sus, "default")
        self.assertNotIn("Csus4sus2", self._get_suggestions_for_chord(results_no_sus, "Csus4"))
        self.assertNotIn("Adimsus2", self._get_suggestions_for_chord(results_no_sus, "Adim"))


    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS)
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_passing_diminished(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {} # Not key dependent
        progression = [
            {"chord": "C", "time": 0.0}, 
            {"chord": "D", "time": 1.0}, # C -> D (whole step)
            {"chord": "F", "time": 2.0},
            {"chord": "G", "time": 3.0}  # F -> G (whole step)
        ]
        results = rule_based.apply_rule_based_flourishes(progression, "default")
        self._assert_suggestions_contain(results, "C", "C#dim") # or Dbdim
        self._assert_suggestions_contain(results, "F", "F#dim") # or Gbdim

        prog_no_whole_step = [{"chord": "C", "time": 0.0}, {"chord": "E", "time": 1.0}]
        results_no_dim = rule_based.apply_rule_based_flourishes(prog_no_whole_step, "default")
        c_suggestions = self._get_suggestions_for_chord(results_no_dim, "C")
        # Check that no dim chord related to C-E is suggested (e.g. C#dim, Ddim, D#dim)
        self.assertFalse(any("dim" in s for s in c_suggestions if s not in ["C", "Csus2", "Csus4", "Cadd9"]))


    def test_empty_progression(self):
        results = rule_based.apply_rule_based_flourishes([], "default")
        self.assertEqual(results, [])

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', {"default": {}})
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_missing_chord_key_in_input(self, mock_detect_key): # Removed mock_config
        mock_detect_key.return_value = {}
        progression = [{"time": 0.0, "note": "C"}] # 'chord' key missing
        results = rule_based.apply_rule_based_flourishes(progression, "default")
        self.assertEqual(results, []) # Should skip items without 'chord'

    @patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', {"non_existent_rules": {}})
    @patch('flourish_engine.rule_based.detect_key_from_chords')
    def test_rule_set_not_found_warning(self, mock_detect_key): # Removed mock_config_const
        mock_detect_key.return_value = {}
        progression = [{"chord": "C", "time": 0.0}]
        # Default config is MOCK_CONFIG_SUBSTITUTIONS['default']
        # If we ask for "unknown_set", it should use default (or empty if default is also missing)
        # The code logs a warning and uses default if rule_set_name is not "default" and not found.
        # If "default" itself is missing from RULE_BASED_SUBSTITUTIONS, it uses {}.
        
        # Case 1: rule_set_name not found, default exists
        with patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', MOCK_CONFIG_SUBSTITUTIONS):
            with self.assertLogs(level='WARNING') as log_capture:
                results = rule_based.apply_rule_based_flourishes(progression, "unknown_set")
            self.assertTrue(any("Rule set 'unknown_set' not found. Using default rules." in msg for msg in log_capture.output))
            self.assertIn("Cadd9", self._get_suggestions_for_chord(results, "C")) # From default

        # Case 2: rule_set_name not found, and "default" is also not in the (mocked) config
        with patch('flourish_engine.rule_based.RULE_BASED_SUBSTITUTIONS', {"other_set": {}}): # No "default"
             with self.assertLogs(level='WARNING') as log_capture: # Warning for unknown_set
                results_no_default = rule_based.apply_rule_based_flourishes(progression, "unknown_set")
             # It will then try to get "default", which is also missing, so substitutions_config becomes {}
             # This means only non-config rules (sus, dim, 7ths if key) apply
             c_suggestions = self._get_suggestions_for_chord(results_no_default, "C")
             self.assertNotIn("Cadd9", c_suggestions) # Cadd9 was from default config
             self.assertIn("Csus2", c_suggestions)


if __name__ == '__main__':
    # This basicConfig is for running the file directly, setUpClass handles `python -m unittest`
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
    unittest.main()
