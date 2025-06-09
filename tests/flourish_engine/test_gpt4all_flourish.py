import unittest
from unittest.mock import patch, MagicMock 
# import sys # No longer needed with direct patching strategy
# import importlib # No longer needed with direct patching strategy

from flourish_engine import gpt4all_flourish

class TestGPT4AllFlourishes(unittest.TestCase):

    # No setUp/tearDown needed for sys.modules and config mocking if directly patching DEFAULT_MODEL_PATH

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', False)
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', None)
    def test_gpt4all_not_available_fallback(self): # Removed mock_default_path_val
        prog = [{"chord": "C", "time": 0.0}]
        results = gpt4all_flourish.suggest_chord_substitutions(prog)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["original_chord"], "C")
        self.assertIn("Cmaj7", results[0]["suggestions"])
        self.assertIn("C9", results[0]["suggestions"])

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', True)
    @patch('flourish_engine.gpt4all_flourish.GPT4All', None) 
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', None) 
    def test_gpt4all_class_is_none_fallback(self): # mock_gpt4all_class removed as GPT4All is replaced by None
        prog = [{"chord": "C", "time": 0.0}]
        results = gpt4all_flourish.suggest_chord_substitutions(prog)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["original_chord"], "C")
        self.assertIn("Cmaj7", results[0]["suggestions"]) 
        self.assertIn("C9", results[0]["suggestions"])

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', True)
    @patch('flourish_engine.gpt4all_flourish.GPT4All') 
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', "dummy/path/model.bin")
    def test_model_load_failure_fallback(self, MockGPT4AllClass): # Removed mock_default_path_val
        MockGPT4AllClass.side_effect = Exception("Model load failed")
        prog = [{"chord": "C", "time": 0.0}]
        # Ensure the module is reloaded if its import-time behavior depends on patched DEFAULT_MODEL_PATH
        # However, patching DEFAULT_MODEL_PATH directly at the module level should affect its value.
        # If issues persist, reload might be needed here too, or ensure patch order is correct.
        results = gpt4all_flourish.suggest_chord_substitutions(prog)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["original_chord"], "C")
        self.assertIn("C7", results[0]["suggestions"]) 
        self.assertIn("Cadd9", results[0]["suggestions"])
        MockGPT4AllClass.assert_called_once_with("dummy/path/model.bin")

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', True)
    @patch('flourish_engine.gpt4all_flourish.GPT4All')
    @patch('flourish_engine.gpt4all_flourish.detect_key_from_chords')
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', "dummy/path/model.bin")
    def test_llm_generation_success(self, mock_detect_key, MockGPT4AllClass): # Removed mock_default_path_val
        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = "Okay, how about G7, or Am?"
        mock_chat_session_cm = MagicMock()
        mock_chat_session_cm.__enter__.return_value = None 
        mock_chat_session_cm.__exit__.return_value = None
        mock_model_instance.chat_session.return_value = mock_chat_session_cm
        
        MockGPT4AllClass.return_value = mock_model_instance
        mock_detect_key.return_value = {"key_root": "C", "key_quality": "major"}

        prog = [{"chord": "C", "time": 0.0}]
        results = gpt4all_flourish.suggest_chord_substitutions(prog)

        MockGPT4AllClass.assert_called_once_with("dummy/path/model.bin")
        mock_model_instance.generate.assert_called_once()
        self.assertIn("key of C major", mock_model_instance.generate.call_args[0][0])
        self.assertIn("chord 'C'", mock_model_instance.generate.call_args[0][0])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["original_chord"], "C")
        self.assertIn("G7", results[0]["suggestions"])
        self.assertIn("Am", results[0]["suggestions"])

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', True)
    @patch('flourish_engine.gpt4all_flourish.GPT4All')
    @patch('flourish_engine.gpt4all_flourish.detect_key_from_chords')
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', "dummy/path/model.bin")
    def test_llm_generation_failure_fallback(self, mock_detect_key, MockGPT4AllClass): # Removed mock_default_path_val
        mock_model_instance = MagicMock()
        mock_model_instance.generate.side_effect = Exception("LLM error")
        mock_chat_session_cm = MagicMock()
        mock_chat_session_cm.__enter__.return_value = None
        mock_chat_session_cm.__exit__.return_value = None
        mock_model_instance.chat_session.return_value = mock_chat_session_cm
        MockGPT4AllClass.return_value = mock_model_instance
        mock_detect_key.return_value = {}

        prog = [{"chord": "Dm", "time": 0.0}]
        results = gpt4all_flourish.suggest_chord_substitutions(prog)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["original_chord"], "Dm")
        self.assertIn("Dmsus", results[0]["suggestions"]) 
        self.assertIn("Dm6", results[0]["suggestions"])

    @patch('flourish_engine.gpt4all_flourish._gpt4all_available', True)
    @patch('flourish_engine.gpt4all_flourish.GPT4All')
    @patch('flourish_engine.gpt4all_flourish.detect_key_from_chords', return_value={})
    @patch('flourish_engine.gpt4all_flourish.DEFAULT_MODEL_PATH', "dummy/path/model.bin")
    def test_response_parsing_and_validation(self, mock_detect_key, MockGPT4AllClass): # Removed mock_default_path_val
        mock_model_instance = MagicMock()
        mock_chat_session_cm = MagicMock()
        mock_chat_session_cm.__enter__.return_value = None
        mock_chat_session_cm.__exit__.return_value = None
        mock_model_instance.chat_session.return_value = mock_chat_session_cm
        MockGPT4AllClass.return_value = mock_model_instance

        responses_and_expected = [
            ("G7, Am7", {"G7", "Am7"}),
            ("Try Cmaj7 or F#m7b5.", {"Cmaj7", "F#m7b5"}),
            ("Maybe Dsus4\nOr perhaps Em7", {"Dsus4", "Em7"}),
            ("Invalid response text here", set()), 
            ("C G Am F", {"C", "G", "Am", "F"}), 
            ("C7b9", {"C7b9"}), 
            ("G/B", {"G/B"}) 
        ]
        
        prog = [{"chord": "X", "time": 0.0}] 

        for resp_str, expected_set in responses_and_expected:
            mock_model_instance.generate.return_value = resp_str
            results = gpt4all_flourish.suggest_chord_substitutions(prog)
            if expected_set: 
                self.assertEqual(results[0]["original_chord"], "X")
                self.assertEqual(set(results[0]["suggestions"]), expected_set)
            else: 
                self.assertEqual(set(results[0]["suggestions"]), {"X"})


if __name__ == '__main__':
    unittest.main()
