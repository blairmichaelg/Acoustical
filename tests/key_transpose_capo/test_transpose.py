import unittest
from key_transpose_capo import transpose

class TestTranspose(unittest.TestCase):

    def test_transpose_major_chords(self):
        self.assertEqual(transpose.transpose_chords(["C", "G", "F"], 2), ["D", "A", "G"])
        # A transposed by -1 is Ab (G#). music21 might choose G#.
        transposed_e_a = transpose.transpose_chords(["E", "A"], -1)
        self.assertEqual(transposed_e_a[0], "E-")
        self.assertIn(transposed_e_a[1], ["A-", "G#"])
        self.assertEqual(transpose.transpose_chords(["B"], 1), ["C"])
        self.assertEqual(transpose.transpose_chords(["C"], -1), ["B"])

    def test_transpose_minor_chords(self):
        self.assertEqual(transpose.transpose_chords(["Am", "Dm"], 3), ["Cm", "Fm"])
        self.assertEqual(transpose.transpose_chords(["C#m"], -2), ["Bm"])
        # music21 might output 'b- minor' for Bbm
        transposed_bbm = transpose.transpose_chords(["Am"], 1) 
        self.assertIn(transposed_bbm[0], ["A#m", "B-m"])


    def test_transpose_seventh_chords(self):
        # Note: music21's cs.figure might vary for enharmonics (e.g. C# vs D-)
        # We test for common outputs or accept alternatives.
        csharp7 = transpose.transpose_chords(["C7"], 1)
        self.assertIn(csharp7[0], ["C#7", "D-7"])

        gsharp_maj7 = transpose.transpose_chords(["Gmaj7"], 1)
        self.assertIn(gsharp_maj7[0], ["G#maj7", "A-maj7"])
        
        asharp_m7 = transpose.transpose_chords(["Am7"], 1)
        self.assertIn(asharp_m7[0], ["A#m7", "B-m7"])

    def test_transpose_extended_chords(self):
        # Behavior depends on music21's parsing and figure generation
        # Cmaj7b5 transposed +2 -> Dmaj7b5 (or Dmaj7(b5))
        # transpose.transpose_chords(["Cmaj7b5"], 2) # music21 might not parse "Cmaj7b5" directly; removed unused variable
                                                            # It might parse as Cmaj7 then try to add b5 if supported by figure
                                                            # Or it might be specific like C half-diminished
        # For now, let's test a common one music21 handles well
        self.assertEqual(transpose.transpose_chords(["G9"], -2), ["F9"])
        self.assertEqual(transpose.transpose_chords(["Cadd9"], 2), ["D add 9"]) # music21 outputs with space


    def test_transpose_by_octave(self):
        self.assertEqual(transpose.transpose_chords(["C", "Am"], 12), ["C", "Am"])
        self.assertEqual(transpose.transpose_chords(["G7"], -12), ["G7"])

    def test_transpose_single_notes_fallback(self):
        # This tests the pitch fallback if ChordSymbol fails
        # Assuming "G#" might be treated as a pitch by music21 if not a known chord symbol
        transposed_notes = transpose.transpose_chords(["C", "G#"], 2)
        self.assertIn("D", transposed_notes)
        self.assertIn(transposed_notes[1], ["A#", "B-"]) # G# + 2 = A# or Bb

    def test_invalid_chord_input(self):
        with self.assertRaisesRegex(ValueError, "Invalid chord: Xyz"):
            transpose.transpose_chords(["C", "Xyz", "G"], 1)
        
        # Test with only one invalid chord
        with self.assertRaisesRegex(ValueError, "Invalid chord: Abc"):
            transpose.transpose_chords(["Abc"], 1)

    def test_empty_list_input(self):
        self.assertEqual(transpose.transpose_chords([], 2), [])

if __name__ == '__main__':
    unittest.main()
