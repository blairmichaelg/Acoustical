import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import importlib # Keep for original_import_module_func if needed by is_available tests

from chord_extraction.essentia_wrapper import EssentiaBackend, register_backend # ESSENTIA_AVAILABLE removed from here
from chord_extraction.backend_registry import unregister_backend_by_method

# Store original import_module at the module level for is_available tests
# This might not be needed if we directly patch ESSENTIA_AVAILABLE for those tests
original_import_module_func = importlib.import_module

class TestEssentiaBackend(unittest.TestCase):

    def setUp(self):
        # Patch ESSENTIA_AVAILABLE to True for most tests, assuming essentia is usable.
        # Individual tests can override this if they need to test the False case.
        self.patcher_essentia_available = patch('chord_extraction.essentia_wrapper.ESSENTIA_AVAILABLE', True)
        self.patcher_essentia_available.start()

        # Patch 'es' module within essentia_wrapper to be a MagicMock.
        # This allows its attributes (like MonoLoader) to be further mocked per test.
        # This patch should be active if ESSENTIA_AVAILABLE is True.
        # We rely on the module-level import of 'es' in essentia_wrapper.py
        self.patcher_es_module = patch('chord_extraction.essentia_wrapper.es', MagicMock(name="mock_es_module_global"))
        self.mock_es_module = self.patcher_es_module.start()


    def tearDown(self):
        unregister_backend_by_method(EssentiaBackend.extract_chords)
        self.patcher_essentia_available.stop()
        self.patcher_es_module.stop()


    def test_is_available_essentia_present(self):
        # Stop the setUp patchers to test is_available's direct dependency on module-level import
        self.patcher_essentia_available.stop()
        self.patcher_es_module.stop()
        
        with patch('chord_extraction.essentia_wrapper.ESSENTIA_AVAILABLE', True):
            self.assertTrue(EssentiaBackend.is_available())
        
        # Restart patchers if they were stopped
        self.patcher_essentia_available.start()
        self.patcher_es_module.start()


    def test_is_available_essentia_absent(self):
        self.patcher_essentia_available.stop()
        self.patcher_es_module.stop()

        with patch('chord_extraction.essentia_wrapper.ESSENTIA_AVAILABLE', False):
            self.assertFalse(EssentiaBackend.is_available())
        
        self.patcher_essentia_available.start()
        self.patcher_es_module.start()


    # The mock_es_module from setUp is active here.
    # We assign specific class mocks to its attributes.
    @patch('chord_extraction.essentia_wrapper.es.ChordsDetectionBeats')
    @patch('chord_extraction.essentia_wrapper.es.RhythmExtractor2013')
    @patch('chord_extraction.essentia_wrapper.es.MonoLoader')
    def test_extract_chords_success(self, MockMonoLoader_class, MockRhythmExtractor_class, MockChordsDetectionBeats_class):
        # ESSENTIA_AVAILABLE is True due to setUp patch.
        # chord_extraction.essentia_wrapper.es is self.mock_es_module.
        # The decorators replace attributes on self.mock_es_module.
        
        mock_mono_loader_instance = MockMonoLoader_class.return_value
        mock_rhythm_extractor_instance = MockRhythmExtractor_class.return_value
        mock_chords_detection_beats_instance = MockChordsDetectionBeats_class.return_value
            
        mock_mono_loader_instance.return_value = np.array([0.0] * 44100, dtype=np.float32) 
        mock_mono_loader_instance.sampleRate = 44100

        dummy_beats = np.array([0.5, 1.0, 1.5, 2.0], dtype=np.float32)
        mock_rhythm_extractor_instance.return_value = (120.0, dummy_beats, 0.9, MagicMock(), MagicMock())

        dummy_essentia_chords_val = ["C:maj", "G:maj", "A:min", "F:maj"] 
        dummy_chord_strength_val = np.array([0.8, 0.7, 0.9, 0.75], dtype=np.float32)
        mock_chords_detection_beats_instance.return_value = (dummy_essentia_chords_val, dummy_chord_strength_val)
        
        register_backend(EssentiaBackend)

        expected_output = [
            {"time": 0.5, "chord": "C"},
            {"time": 1.0, "chord": "G"},
            {"time": 1.5, "chord": "Am"},
            {"time": 2.0, "chord": "F"}
        ]
        result = EssentiaBackend.extract_chords("dummy.wav")
        self.assertEqual(result, expected_output)

        MockMonoLoader_class.assert_called_once_with(filename="dummy.wav")
        MockRhythmExtractor_class.assert_called_once_with(method="multifeature")
        MockChordsDetectionBeats_class.assert_called_once_with(hopSize=2048, windowSize=2048)

    def test_extract_chords_not_available(self):
        # Override setUp patch for ESSENTIA_AVAILABLE
        self.patcher_essentia_available.stop()
        with patch('chord_extraction.essentia_wrapper.ESSENTIA_AVAILABLE', False):
            with self.assertRaisesRegex(ImportError, "Essentia library is not installed or available."):
                EssentiaBackend.extract_chords("dummy.wav")
        self.patcher_essentia_available.start() # Restart for other tests

    @patch('chord_extraction.essentia_wrapper.es.MonoLoader')
    def test_extract_chords_essentia_processing_error(self, MockMonoLoader_class):
        # ESSENTIA_AVAILABLE is True from setUp. es is self.mock_es_module.
        mock_mono_loader_instance = MockMonoLoader_class.return_value
        mock_mono_loader_instance.side_effect = Exception("Essentia internal error")
            
        register_backend(EssentiaBackend)
        with self.assertRaisesRegex(RuntimeError, "Essentia chord extraction failed"):
            EssentiaBackend.extract_chords("dummy.wav")

    @patch('chord_extraction.essentia_wrapper.es.RhythmExtractor2013')
    @patch('chord_extraction.essentia_wrapper.es.MonoLoader')
    def test_extract_chords_no_beats_detected(self, MockMonoLoader_class, MockRhythmExtractor_class):
        # ESSENTIA_AVAILABLE is True from setUp. es is self.mock_es_module.
        mock_mono_loader_instance = MockMonoLoader_class.return_value
        mock_rhythm_extractor_instance = MockRhythmExtractor_class.return_value

        mock_mono_loader_instance.return_value = np.array([0.0] * 44100, dtype=np.float32)
        mock_rhythm_extractor_instance.return_value = (120.0, np.array([], dtype=np.float32), 0.0, MagicMock(), MagicMock()) # No beats
            
        register_backend(EssentiaBackend)
        result = EssentiaBackend.extract_chords("dummy.wav")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
