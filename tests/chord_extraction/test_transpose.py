import unittest
from key_transpose_capo.transpose import transpose_chords

class TestTranspose(unittest.TestCase):
    def test_transpose_up(self):
        chords = ["C", "G", "Am", "F"]
        expected = ["D", "A", "Bm", "G"]  # Example: up 2 semitones
        result = transpose_chords(chords, 2)
        self.assertEqual(result, expected)

    def test_transpose_down(self):
        chords = ["C", "G", "Am", "F"]
        expected = ["A", "E", "F#m", "D"]  # Example: down 3 semitones
        result = transpose_chords(chords, -3)
        self.assertEqual(result, expected)

    def test_invalid_chord(self):
        chords = ["C", "???", "Am"]
        with self.assertRaises(Exception):
            transpose_chords(chords, 1)

if __name__ == "__main__":
    unittest.main()
