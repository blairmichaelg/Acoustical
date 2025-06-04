import unittest
import logging
from typing import List, Optional
from music_theory.fretboard import Fretboard
from music_theory import utils as mtu # For note value constants if needed

class TestFretboard(unittest.TestCase):

    def test_initialization_default(self):
        fb = Fretboard()
        self.assertEqual(fb.num_strings, 6)
        self.assertEqual(fb.num_frets, 22)
        # E A D G B E -> 4, 9, 2, 7, 11, 4
        expected_open_values = [mtu.get_note_value(n) for n in ["E", "A", "D", "G", "B", "E"]]
        self.assertEqual(fb.string_open_notes_values, expected_open_values)
        self.assertEqual(fb.notes_on_fret[0][0], mtu.get_note_value("E")) # Low E open
        self.assertEqual(fb.notes_on_fret[5][0], mtu.get_note_value("E")) # High E open
        self.assertEqual(fb.notes_on_fret[0][12], mtu.get_note_value("E")) # Low E 12th fret

    def test_initialization_custom_tuning(self):
        drop_d_tuning = ["D", "A", "D", "G", "B", "E"] # Octaves ignored by get_note_value
        fb = Fretboard(tuning=drop_d_tuning, num_frets=20)
        self.assertEqual(fb.num_strings, 6)
        self.assertEqual(fb.num_frets, 20)
        expected_open_values = [mtu.get_note_value(n) for n in drop_d_tuning]
        self.assertEqual(fb.string_open_notes_values, expected_open_values)
        self.assertEqual(fb.notes_on_fret[0][0], mtu.get_note_value("D"))

    def test_initialization_invalid_tuning_string(self):
        invalid_tuning = ["E", "X", "D", "G", "B", "E"]
        with self.assertLogs(level='WARNING') as log_capture:
            fb = Fretboard(tuning=invalid_tuning)
            self.assertIsNone(fb.string_open_notes_values[1]) # "X" string
            self.assertTrue(any("Invalid open string note 'X'" in message for message in log_capture.output))
            # Check that notes on the invalid string are None
            self.assertIsNone(fb.notes_on_fret[1][0])
            self.assertIsNone(fb.notes_on_fret[1][5])
            # Check a valid string is still processed
            self.assertEqual(fb.notes_on_fret[0][0], mtu.get_note_value("E"))


    def test_get_note_at(self):
        fb = Fretboard()
        self.assertEqual(fb.get_note_at(0, 0), mtu.get_note_value("E"))  # Low E
        self.assertEqual(fb.get_note_at(0, 5), mtu.get_note_value("A"))  # Low E, 5th fret = A
        self.assertEqual(fb.get_note_at(1, 5), mtu.get_note_value("D"))  # A string, 5th fret = D
        self.assertEqual(fb.get_note_at(5, 12), mtu.get_note_value("E")) # High E, 12th fret

        # Out of bounds
        self.assertIsNone(fb.get_note_at(-1, 0))
        self.assertIsNone(fb.get_note_at(6, 0))
        self.assertIsNone(fb.get_note_at(0, -1))
        self.assertIsNone(fb.get_note_at(0, fb.num_frets + 1))

    def test_get_note_name_at(self):
        fb = Fretboard()
        self.assertEqual(fb.get_note_name_at(0, 1), "F") # E string, 1st fret
        self.assertEqual(fb.get_note_name_at(1, 1), "A#") # A string, 1st fret (A#)
        self.assertEqual(fb.get_note_name_at(1, 1, prefer_sharp=False), "Bb")

    def test_find_note_positions_standard_tuning(self):
        fb = Fretboard()
        # Test finding "E"
        e_positions = sorted(fb.find_note_positions("E"))
        expected_e = sorted([(0,0), (0,12), (0,24) if fb.num_frets >=24 else (0,0), # Filter out of bounds
                               (1,7), (1,19),
                               (2,2), (2,14),
                               (3,9), (3,21),
                               (4,5), (4,17),
                               (5,0), (5,12), (5,24) if fb.num_frets >=24 else (5,0)])
        # Filter expected positions based on actual num_frets
        expected_e_filtered = sorted(list(set([(s,f) for s,f in expected_e if f <= fb.num_frets])))
        self.assertEqual(e_positions, expected_e_filtered)

        # Test finding "C#"
        c_sharp_positions = sorted(fb.find_note_positions("C#"))
        expected_c_sharp = sorted([(0,9), (0,21), (1,4), (1,16), (2,11), (2,23) if fb.num_frets >=23 else (2,11), (3,6), (3,18), (4,2), (4,14), (5,9), (5,21)])
        expected_c_sharp_filtered = sorted(list(set([(s,f) for s,f in expected_c_sharp if f <= fb.num_frets])))
        self.assertEqual(c_sharp_positions, expected_c_sharp_filtered)

        # Test with max_fret
        g_positions_max_5 = sorted(fb.find_note_positions("G", max_fret=5))
        expected_g_max_5 = sorted([(0,3), (1,10) if 5>=10 else (0,3), (2,5), (3,0), (4,8) if 5>=8 else (0,3), (5,3)]) # Re-eval this logic
        # Corrected expected_g_max_5
        # String 0 (E): G is fret 3. (0,3)
        # String 1 (A): G is fret 10. (skip as > 5)
        # String 2 (D): G is fret 5. (2,5)
        # String 3 (G): G is fret 0. (3,0)
        # String 4 (B): G is fret 8. (skip as > 5)
        # String 5 (E): G is fret 3. (5,3)
        expected_g_max_5_corrected = sorted([(0,3), (2,5), (3,0), (5,3)])
        self.assertEqual(g_positions_max_5, expected_g_max_5_corrected)


    def test_find_note_positions_by_value(self):
        fb = Fretboard()
        c_val = mtu.get_note_value("C")
        self.assertIsNotNone(c_val)
        c_positions_val = sorted(fb.find_note_positions(c_val))
        c_positions_name = sorted(fb.find_note_positions("C"))
        self.assertEqual(c_positions_val, c_positions_name)

    def test_find_note_positions_invalid_note(self):
        fb = Fretboard()
        self.assertEqual(fb.find_note_positions("X"), [])
        self.assertEqual(fb.find_note_positions(None), []) # type: ignore
        self.assertEqual(fb.find_note_positions(1.5), []) # type: ignore

    def test_find_note_positions_drop_d(self):
        drop_d_tuning = ["D", "A", "D", "G", "B", "E"]
        fb_drop_d = Fretboard(tuning=drop_d_tuning)
        d_positions = sorted(fb_drop_d.find_note_positions("D"))
        # Expected Ds in Drop D (up to default 22 frets):
        # S0 (D): 0, 12
        # S1 (A): 5, 17
        # S2 (D): 0, 12
        # S3 (G): 7, 19
        # S4 (B): 3, 15
        # S5 (E): 10, 22
        expected_d_drop_d = sorted([
            (0,0), (0,12), (1,5), (1,17), (2,0), (2,12),
            (3,7), (3,19), (4,3), (4,15), (5,10), (5,22)
        ])
        self.assertEqual(d_positions, expected_d_drop_d)

if __name__ == '__main__':
    unittest.main()
