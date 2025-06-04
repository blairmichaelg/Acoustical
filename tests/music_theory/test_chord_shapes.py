import unittest
import logging
from music_theory import chord_shapes as cs
from music_theory import utils as mtu

class TestChordShapes(unittest.TestCase):

    def test_chord_shape_repr(self):
        shape = cs.ChordShape("C Major Open", "C", "maj", fingerings=[(0,-1,-1),(1,3,3),(2,2,2),(3,0,0),(4,1,1),(5,0,0)])
        self.assertIn("name='C Major Open'", repr(shape))
        self.assertIn("template_root='C'", repr(shape))
        self.assertIn("type='maj'", repr(shape))

    def test_transpose_shape_e_major_to_gmajor(self):
        e_maj_template = None
        for shape in cs.COMMON_CHORD_SHAPE_TEMPLATES.get("maj", []):
            if shape.name == "E Shape Barre" and shape.template_root_note_str == "E":
                e_maj_template = shape
                break
        self.assertIsNotNone(e_maj_template, "E Shape Barre template for major not found.")
        
        if e_maj_template:
            g_maj_transposed = cs._transpose_shape(e_maj_template, "G")
            self.assertIsNotNone(g_maj_transposed)
            if g_maj_transposed:
                self.assertEqual(g_maj_transposed.template_root_note_str, "G")
                self.assertEqual(g_maj_transposed.chord_type, "maj")
                self.assertEqual(g_maj_transposed.base_fret_of_template, 3) # G is 3 semitones above E
                # Original E shape: (0,0,1),(1,2,3),(2,2,4),(3,1,2),(4,0,1),(5,0,1)
                # Transposed to G (offset +3):
                expected_fingerings = [(0,3,1),(1,5,3),(2,5,4),(3,4,2),(4,3,1),(5,3,1)]
                self.assertEqual(g_maj_transposed.fingerings, expected_fingerings)
                self.assertEqual(g_maj_transposed.barre_strings_offset, [0,1,2,3,4,5])

    def test_transpose_shape_a_minor_to_csharp_minor(self):
        am_template = None
        for shape in cs.COMMON_CHORD_SHAPE_TEMPLATES.get("min", []):
            if shape.name == "Am Shape Barre" and shape.template_root_note_str == "A":
                am_template = shape
                break
        self.assertIsNotNone(am_template, "Am Shape Barre template for minor not found.")

        if am_template:
            csharp_m_transposed = cs._transpose_shape(am_template, "C#")
            self.assertIsNotNone(csharp_m_transposed)
            if csharp_m_transposed:
                self.assertEqual(csharp_m_transposed.template_root_note_str, "C#")
                self.assertEqual(csharp_m_transposed.chord_type, "min")
                self.assertEqual(csharp_m_transposed.base_fret_of_template, 4) # C# is 4 semitones above A
                # Original Am shape: (0,-1,-1),(1,0,1),(2,2,3),(3,2,4),(4,1,2),(5,0,1)
                # Transposed to C#m (offset +4):
                expected_fingerings = [(0,-1,-1),(1,4,1),(2,6,3),(3,6,4),(4,5,2),(5,4,1)]
                self.assertEqual(csharp_m_transposed.fingerings, expected_fingerings)

    def test_transpose_non_movable_shape(self):
        c_maj_open_template = cs.COMMON_CHORD_SHAPE_TEMPLATES["maj"][2] # C Major Open
        self.assertFalse(c_maj_open_template.is_movable)
        transposed = cs._transpose_shape(c_maj_open_template, "D")
        self.assertIsNone(transposed)

    def test_transpose_out_of_bounds(self):
        e_maj_template = cs.COMMON_CHORD_SHAPE_TEMPLATES["maj"][0] # E Shape Barre
        transposed = cs._transpose_shape(e_maj_template, "D#") # D# is 11 semitones below E, or 1 above. E is 4, D# is 3. Offset -1 or +11.
                                                              # E(4) to D#(3) is -1 or +11. Offset = (3-4+12)%12 = 11. Base fret 0+11=11. OK.
                                                              # E(4) to E(4) (1 octave higher) -> offset 12. Base fret 0+12=12. OK.
                                                              # E(4) to F(5) (1 octave higher) -> offset 13. Base fret 0+13=13. OK.
        # Try transposing E shape so high it goes beyond fret 15 limit
        # Example: E (val 4) to D (val 2) one octave up. D is 10 semitones higher than E (4->2 is -2 or +10)
        # Target D (value 2). E (value 4). (2 - 4 + 12) % 12 = 10. Base fret 0+10=10.
        # Let's try to make it go beyond 15.
        # If template is E (val 4), target root is G# (val 8) an octave higher. (8-4+12)%12 = 4.  This is G# at fret 4.
        # To exceed 15, need a large interval.
        # E (val 4) to D (val 2) two octaves up. (2 - 4 + 24) % 12 = 10. Still 10.
        # The transposition_offset is always % 12. new_base_fret = template.base_fret_of_template + transposition_offset
        # If base_fret_of_template is 0, new_base_fret will be 0-11.
        # The check is `if new_base_fret < 0 or new_base_fret > 15`.
        # This means we need a template whose base_fret_of_template + transposition_offset > 15.
        # Our E and A shape templates have base_fret_of_template = 0.
        # So, this test as is won't exceed the limit unless we define a template with a higher base_fret_of_template.
        # For now, let's assume the current templates.
        # A transposition that would result in a high fret: E shape to Eb (val 3). (3-4+12)%12 = 11. Base fret 11.
        transposed_high = cs._transpose_shape(e_maj_template, "Eb")
        self.assertIsNotNone(transposed_high)
        if transposed_high:
            self.assertEqual(transposed_high.base_fret_of_template, 11)

        # To truly test out of bounds, we'd need a shape that starts higher or transpose further.
        # Let's simulate a shape that starts at fret 5.
        high_template = cs.ChordShape("High E Barre", "E", "maj", e_maj_template.fingerings, base_fret_of_template=5, is_movable=True)
        transposed_too_high = cs._transpose_shape(high_template, "D") # E(5th fret) to D (10 semitones higher) -> 5 + 10 = 15. Still OK.
        transposed_too_high_2 = cs._transpose_shape(high_template, "Eb") # E(5th fret) to Eb (11 semitones higher) -> 5 + 11 = 16. Should be None.
        self.assertIsNone(transposed_too_high_2)


    def test_get_shapes_for_chord_open(self):
        c_maj_shapes = cs.get_shapes_for_chord("C", "maj")
        self.assertTrue(any(s.name == "C Major Open" for s in c_maj_shapes))
        am_shapes = cs.get_shapes_for_chord("A", "min")
        self.assertTrue(any(s.name == "Am Minor Open" for s in am_shapes))

    def test_get_shapes_for_chord_transposed_barre(self):
        f_maj_shapes = cs.get_shapes_for_chord("F", "maj") # Should use E Shape Barre
        self.assertTrue(any(s.name == "E Shape Barre for F" and s.base_fret_of_template == 1 for s in f_maj_shapes))

        bb_maj_shapes = cs.get_shapes_for_chord("Bb", "maj") # Should use A Shape Barre (and E shape)
        self.assertTrue(any(s.name == "A Shape Barre for Bb" and s.base_fret_of_template == 1 for s in bb_maj_shapes))
        self.assertTrue(any(s.name == "E Shape Barre for Bb" and s.base_fret_of_template == 6 for s in bb_maj_shapes))

        c_sharp_min_shapes = cs.get_shapes_for_chord("C#", "min")
        self.assertTrue(any(s.name == "Am Shape Barre for C#" and s.base_fret_of_template == 4 for s in c_sharp_min_shapes))
        self.assertTrue(any(s.name == "Em Shape Barre for C#" and s.base_fret_of_template == 9 for s in c_sharp_min_shapes))

    def test_get_shapes_for_7th_chords(self):
        f7_shapes = cs.get_shapes_for_chord("F", "7")
        self.assertTrue(any(s.name == "E7 Shape Barre for F" and s.base_fret_of_template == 1 for s in f7_shapes))

        b_maj7_shapes = cs.get_shapes_for_chord("B", "maj7") # Should use A-shape maj7 barre
        self.assertTrue(any(s.name == "A Shape maj7 Barre for B" and s.base_fret_of_template == 2 for s in b_maj7_shapes))
        self.assertTrue(any(s.name == "E Shape maj7 Barre for B" and s.base_fret_of_template == 7 for s in b_maj7_shapes))


    def test_get_shapes_unknown_type(self):
        shapes = cs.get_shapes_for_chord("C", "unknown")
        self.assertEqual(len(shapes), 0)

    def test_get_shapes_normalization(self):
        g_maj_shapes1 = cs.get_shapes_for_chord("G", "major")
        g_maj_shapes2 = cs.get_shapes_for_chord("G", "maj")
        g_maj_shapes3 = cs.get_shapes_for_chord("G", "")
        self.assertEqual(len(g_maj_shapes1), len(g_maj_shapes2))
        self.assertEqual(len(g_maj_shapes1), len(g_maj_shapes3))
        self.assertTrue(any(s.name == "G Major Open" for s in g_maj_shapes1))

        d_min_shapes1 = cs.get_shapes_for_chord("D", "minor")
        d_min_shapes2 = cs.get_shapes_for_chord("D", "m")
        self.assertEqual(len(d_min_shapes1), len(d_min_shapes2))
        self.assertTrue(any(s.name == "Dm Minor Open" for s in d_min_shapes1))


if __name__ == '__main__':
    unittest.main()
