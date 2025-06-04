import unittest
from unittest.mock import patch, MagicMock

from chord_extraction.backend_registry import (
    ChordExtractionBackend,
    register_backend,
    register_plugin_backend,
    unregister_backend_by_method,
    get_registered_plugins,
    extract_chords_with_fallback,
    _registered_plugins # For direct manipulation in setup/teardown for clean tests
)

# Dummy Backend for testing
class DummyBackendOne(ChordExtractionBackend):
    name = "dummy_one"
    @classmethod
    def extract_chords(cls, audio_path: str):
        return [{"time": 0, "chord": "C from DummyOne"}]

class DummyBackendTwo(ChordExtractionBackend):
    name = "dummy_two"
    @classmethod
    def extract_chords(cls, audio_path: str):
        return [{"time": 1, "chord": "G from DummyTwo"}]

def dummy_plugin_func(audio_path: str):
    return [{"time": 2, "chord": "Am from DummyPluginFunc"}]


class TestBackendRegistry(unittest.TestCase):

    def setUp(self):
        # Clear the global registry before each test for isolation
        self._original_plugins = list(_registered_plugins) # shallow copy
        _registered_plugins.clear()

    def tearDown(self):
        # Restore original plugins
        _registered_plugins.clear()
        _registered_plugins.extend(self._original_plugins)

    def test_register_backend_class(self):
        register_backend(DummyBackendOne)
        self.assertIn(DummyBackendOne.extract_chords, get_registered_plugins())
        # Test duplicate registration avoidance
        initial_len = len(get_registered_plugins())
        register_backend(DummyBackendOne) # Register again
        self.assertEqual(len(get_registered_plugins()), initial_len)

    def test_register_plugin_backend_callable(self):
        register_plugin_backend(dummy_plugin_func)
        self.assertIn(dummy_plugin_func, get_registered_plugins())

    def test_unregister_backend_by_method(self):
        register_backend(DummyBackendOne)
        self.assertIn(DummyBackendOne.extract_chords, get_registered_plugins())
        unregister_backend_by_method(DummyBackendOne.extract_chords)
        self.assertNotIn(DummyBackendOne.extract_chords, get_registered_plugins())
        # Test unregistering non-existent
        unregister_backend_by_method(DummyBackendTwo.extract_chords) # Should not error

    def test_get_registered_plugins(self):
        self.assertEqual(get_registered_plugins(), [])
        register_backend(DummyBackendOne)
        self.assertEqual(get_registered_plugins(), [DummyBackendOne.extract_chords])

    @patch('chord_extraction.chordino_wrapper.ChordinoBackend.extract_chords')
    @patch('chord_extraction.autochord_util.AutochordBackend.extract_chords')
    @patch('chord_extraction.chord_extractor_util.ChordExtractorBackend.extract_chords')
    def test_extract_chords_with_fallback_no_backends_available(self, mock_ce, mock_auto, mock_chordino):
        mock_chordino.side_effect = ImportError("Chordino unavailable")
        mock_auto.side_effect = ImportError("Autochord unavailable")
        mock_ce.side_effect = ImportError("ChordExtractor unavailable")
        # _registered_plugins is already empty due to setUp
        
        with self.assertRaisesRegex(RuntimeError, "All chord extraction backends failed"):
            extract_chords_with_fallback("dummy.wav")

    @patch('chord_extraction.chordino_wrapper.ChordinoBackend.extract_chords')
    @patch('chord_extraction.autochord_util.AutochordBackend.extract_chords')
    @patch('chord_extraction.chord_extractor_util.ChordExtractorBackend.extract_chords')
    def test_extract_chords_with_fallback_chordino_succeeds(self, mock_ce, mock_auto, mock_chordino):
        expected_result = [{"time": 0, "chord": "C from Chordino"}]
        mock_chordino.return_value = expected_result
        
        result = extract_chords_with_fallback("dummy.wav")
        self.assertEqual(result, expected_result)
        mock_chordino.assert_called_once()
        mock_auto.assert_not_called()
        mock_ce.assert_not_called()

    @patch('chord_extraction.chordino_wrapper.ChordinoBackend.extract_chords')
    @patch('chord_extraction.autochord_util.AutochordBackend.extract_chords')
    @patch('chord_extraction.chord_extractor_util.ChordExtractorBackend.extract_chords')
    def test_extract_chords_with_fallback_autochord_succeeds(self, mock_ce, mock_auto, mock_chordino):
        mock_chordino.side_effect = Exception("Chordino failed")
        expected_result = [{"time": 0, "chord": "C from Autochord"}]
        mock_auto.return_value = expected_result
        
        result = extract_chords_with_fallback("dummy.wav")
        self.assertEqual(result, expected_result)
        mock_chordino.assert_called_once()
        mock_auto.assert_called_once()
        mock_ce.assert_not_called()

    @patch('chord_extraction.chordino_wrapper.ChordinoBackend.extract_chords')
    @patch('chord_extraction.autochord_util.AutochordBackend.extract_chords')
    @patch('chord_extraction.chord_extractor_util.ChordExtractorBackend.extract_chords')
    def test_extract_chords_with_fallback_plugin_succeeds(self, mock_ce, mock_auto, mock_chordino):
        mock_chordino.side_effect = Exception("Chordino failed")
        mock_auto.side_effect = Exception("Autochord failed")
        mock_ce.side_effect = Exception("ChordExtractor failed")
        
        expected_result = [{"time": 0, "chord": "C from Plugin"}]
        mock_plugin = MagicMock(return_value=expected_result)
        register_plugin_backend(mock_plugin)
        
        result = extract_chords_with_fallback("dummy.wav")
        self.assertEqual(result, expected_result)
        mock_plugin.assert_called_once()

if __name__ == '__main__':
    unittest.main()
