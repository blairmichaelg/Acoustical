import unittest
from music_theory import utils as mtu

class TestMusicTheoryUtils(unittest.TestCase):

    def test_get_note_value(self):
        self.assertEqual(mtu.get_note_value("C"), 0)
        self.assertEqual(mtu.get_note_value("C#"), 1)
        self.assertEqual(mtu.get_note_value("Db"), 1)
        self.assertEqual(mtu.get_note_value("D"), 2)
        self.assertEqual(mtu.get_note_value("B"), 11)
        self.assertEqual(mtu.get_note_value("H"), 11) # German B
        self.assertEqual(mtu.get_note_value("c"), 0)
        self.assertEqual(mtu.get_note_value("db"), 1)
        self.assertIsNone(mtu.get_note_value("X"))
        self.assertIsNone(mtu.get_note_value("C##"))
        self.assertIsNone(mtu.get_note_value(""))

    def test_get_note_name(self):
        self.assertEqual(mtu.get_note_name(0), "C")
        self.assertEqual(mtu.get_note_name(1), "C#")
        self.assertEqual(mtu.get_note_name(1, prefer_sharp=False), "Db")
        self.assertEqual(mtu.get_note_name(11), "B")
        self.assertEqual(mtu.get_note_name(12), "C") # Octave wrap
        self.assertEqual(mtu.get_note_name(-1), "B") # Negative wrap

    def test_parse_chord_to_notes_major_triads(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("C")), {"C", "E", "G"})
        self.assertEqual(set(mtu.parse_chord_to_notes("G")), {"G", "B", "D"})
        self.assertEqual(set(mtu.parse_chord_to_notes("F#")), {"F#", "A#", "C#"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Db", prefer_sharp_for_output=False)), {"Db", "F", "Ab"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Cmaj")), {"C", "E", "G"})


    def test_parse_chord_to_notes_minor_triads(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("Am")), {"A", "C", "E"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Emin")), {"E", "G", "B"})
        self.assertEqual(set(mtu.parse_chord_to_notes("C#m")), {"C#", "E", "G#"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Abm", prefer_sharp_for_output=False)), {"Ab", "Cb", "Eb"})


    def test_parse_chord_to_notes_dominant_7ths(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("C7")), {"C", "E", "G", "Bb"})
        self.assertEqual(set(mtu.parse_chord_to_notes("G7")), {"G", "B", "D", "F"})
        self.assertEqual(set(mtu.parse_chord_to_notes("F#7")), {"F#", "A#", "C#", "E"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Bb7", prefer_sharp_for_output=False)), {"Bb", "D", "F", "Ab"})

    def test_parse_chord_to_notes_major_7ths(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("Cmaj7")), {"C", "E", "G", "B"})
        self.assertEqual(set(mtu.parse_chord_to_notes("GM7")), {"G", "B", "D", "F#"})
        self.assertEqual(set(mtu.parse_chord_to_notes("F#maj7")), {"F#", "A#", "C#", "E#"}) # E# is F
        self.assertEqual(set(mtu.parse_chord_to_notes("Dbmaj7", prefer_sharp_for_output=False)), {"Db", "F", "Ab", "C"})

    def test_parse_chord_to_notes_minor_7ths(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("Am7")), {"A", "C", "E", "G"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Emin7")), {"E", "G", "B", "D"})
        self.assertEqual(set(mtu.parse_chord_to_notes("C#m7")), {"C#", "E", "G#", "B"})

    def test_parse_chord_to_notes_dim_aug_sus(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("Cdim")), {"C", "Eb", "Gb"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Caug")), {"C", "E", "G#"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Csus4")), {"C", "F", "G"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Gsus2")), {"G", "A", "D"})

    def test_parse_chord_to_notes_m7b5_dim7(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("Bm7b5", prefer_sharp_for_output=False)), {"B", "D", "F", "A"}) # B D F A
        self.assertEqual(set(mtu.parse_chord_to_notes("Cdim7", prefer_sharp_for_output=False)), {"C", "Eb", "Gb", "Bbb"}) # C Eb Gb A (Bbb is A)

    def test_parse_chord_to_notes_6ths_9ths_add9(self):
        self.assertEqual(set(mtu.parse_chord_to_notes("C6")), {"C", "E", "G", "A"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Am6")), {"A", "C", "E", "F#"})
        self.assertEqual(set(mtu.parse_chord_to_notes("C9")), {"C", "E", "G", "Bb", "D"}) # D is 9th
        self.assertEqual(set(mtu.parse_chord_to_notes("Cmaj9")), {"C", "E", "G", "B", "D"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Cm9")), {"C", "Eb", "G", "Bb", "D"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Cadd9")), {"C", "E", "G", "D"})
        self.assertEqual(set(mtu.parse_chord_to_notes("Cmadd9")), {"C", "Eb", "G", "D"})


    def test_parse_chord_to_notes_invalid(self):
        self.assertEqual(mtu.parse_chord_to_notes("Cxyz"), ["C"]) # Returns root
        self.assertEqual(mtu.parse_chord_to_notes("Hmaj7"), ["B"]) # H is B, but Hmaj7 quality is unknown
        self.assertEqual(mtu.parse_chord_to_notes("Xyz"), ["Xyz"]) # Unparseable root

    def test_generate_scale_major(self):
        self.assertEqual(mtu.generate_scale("C", "major"), ["C", "D", "E", "F", "G", "A", "B"])
        self.assertEqual(mtu.generate_scale("G", "major"), ["G", "A", "B", "C", "D", "E", "F#"])
        self.assertEqual(mtu.generate_scale("F", "major"), ["F", "G", "A", "Bb", "C", "D", "E"]) # Check Bb
        self.assertEqual(mtu.generate_scale("Db", "major"), ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"])

    def test_generate_scale_minor(self): # Natural minor
        self.assertEqual(mtu.generate_scale("A", "minor"), ["A", "B", "C", "D", "E", "F", "G"])
        self.assertEqual(mtu.generate_scale("E", "minor"), ["E", "F#", "G", "A", "B", "C", "D"])
        self.assertEqual(mtu.generate_scale("C", "minor"), ["C", "D", "Eb", "F", "G", "Ab", "Bb"])

    def test_generate_scale_other_types(self):
        self.assertEqual(mtu.generate_scale("A", "harmonic_minor"), ["A", "B", "C", "D", "E", "F", "G#"])
        self.assertEqual(mtu.generate_scale("C", "dorian"), ["C", "D", "Eb", "F", "G", "A", "Bb"])
        self.assertEqual(mtu.generate_scale("C", "pentatonic_major"), ["C", "D", "E", "G", "A"])
        self.assertEqual(mtu.generate_scale("A", "blues"), ["A", "C", "D", "Eb", "E", "G"])


    def test_generate_scale_invalid(self):
        self.assertEqual(mtu.generate_scale("X", "major"), [])
        # Test unknown scale type (should default to major and log warning)
        with self.assertLogs(level='WARNING') as log_capture:
            result = mtu.generate_scale("C", "unknown_scale")
            self.assertEqual(result, ["C", "D", "E", "F", "G", "A", "B"]) # Defaults to C major
            self.assertTrue(any("Unknown scale type: unknown_scale" in message for message in log_capture.output))


    def test_calculate_interval(self):
        self.assertEqual(mtu.calculate_interval("C", "C"), "P1")
        self.assertEqual(mtu.calculate_interval("C", "Db"), "m2")
        self.assertEqual(mtu.calculate_interval("C", "D"), "M2")
        self.assertEqual(mtu.calculate_interval("C", "Eb"), "m3")
        self.assertEqual(mtu.calculate_interval("C", "E"), "M3")
        self.assertEqual(mtu.calculate_interval("C", "F"), "P4")
        self.assertEqual(mtu.calculate_interval("C", "F#"), "A4/d5")
        self.assertEqual(mtu.calculate_interval("C", "G"), "P5")
        self.assertEqual(mtu.calculate_interval("C", "Ab"), "m6")
        self.assertEqual(mtu.calculate_interval("C", "A"), "M6")
        self.assertEqual(mtu.calculate_interval("C", "Bb"), "m7")
        self.assertEqual(mtu.calculate_interval("C", "B"), "M7")
        self.assertEqual(mtu.calculate_interval("G", "C"), "P4") # G up to C is P4
        self.assertIsNone(mtu.calculate_interval("C", "X"))

if __name__ == '__main__':
    unittest.main()
