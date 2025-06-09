import unittest
# from unittest.mock import patch # Not used
# import logging # Not used

from flourish_engine.magenta_flourish import generate_magenta_flourish

class TestMagentaFlourish(unittest.TestCase):

    def test_placeholder_suggestions(self):
        chord_frames = ["C", "G", "Am", "F"]
        expected_suggestions = [
            "(Magenta unavailable) Consider embellishing C with arpeggios or passing tones.",
            "(Magenta unavailable) Consider embellishing G with arpeggios or passing tones.",
            "(Magenta unavailable) Consider embellishing Am with arpeggios or passing tones.",
            "(Magenta unavailable) Consider embellishing F with arpeggios or passing tones."
        ]
        
        # Use assertLogs to check for the warning message
        with self.assertLogs('flourish_engine.magenta_flourish', level='WARNING') as cm:
            results = generate_magenta_flourish(chord_frames)
            self.assertEqual(results, expected_suggestions)
            self.assertEqual(len(cm.output), 1)
            self.assertIn("Magenta improv_rnn integration is not implemented. Returning static suggestions.", cm.output[0])

    def test_empty_chord_frames(self):
        chord_frames = []
        with self.assertLogs('flourish_engine.magenta_flourish', level='WARNING') as cm:
            results = generate_magenta_flourish(chord_frames)
            self.assertEqual(results, [])
            self.assertEqual(len(cm.output), 1)
            self.assertIn("Magenta improv_rnn integration is not implemented. Returning static suggestions.", cm.output[0])

if __name__ == '__main__':
    unittest.main()
