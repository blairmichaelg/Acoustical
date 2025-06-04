import unittest
from key_transpose_capo import capo_advisor

class TestCapoAdvisor(unittest.TestCase):

    def test_recommend_capo_all_open_no_capo(self):
        chords = ["C", "G", "Am", "F"] # F is not in the default small open set, but C,G,Am are
        # Default open_chords: {"C", "D", "E", "G", "A", "Em", "Am", "Dm"}
        # With expanded open_chords in capo_advisor.py, F is still not "open" by default.
        # Capo 0: C, G, Am, F (Score: 1 for F)
        # Capo 1 (transposed down by 1): B, F#, G#m, E (Score: 1 for B, F#, G#m) - assuming E is open
        # Capo 2 (transposed down by 2): Bb, F, Gm, Eb (Score: many non-open)
        # Expected: Capo 0, as it has the most open chords (or fewest non-open)
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 0)
        self.assertEqual(transposed_chords, ["C", "G", "Am", "F"])

    def test_recommend_capo_favor_capo_1(self):
        # Sounding chords: Db, Ab, Bbm, Gb
        # Capo 1, shapes: C, G, Am, F
        chords = ["Db", "Ab", "Bbm", "Gb"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 1)
        # Transposing Db down by 1 gives C, Ab down by 1 gives G, etc.
        self.assertEqual(set(transposed_chords), set(["C", "G", "Am", "F"]))


    def test_recommend_capo_favor_capo_3(self):
        # Sounding chords: Eb, Bb, Cm, Ab
        # Capo 3, shapes: C, G, Am, F
        chords = ["Eb", "Bb", "Cm", "Ab"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 3)
        self.assertEqual(set(transposed_chords), set(["C", "G", "Am", "F"]))

    def test_progression_with_some_non_open(self):
        # Sounding: F#, B, C#m, G#m
        # Capo 0: F#, B, C#m, G#m (0 open from small set, maybe B if B is added to open)
        # Capo 1 (shapes F, Bb, Cm, Gm): F is open. Score = 3
        # Capo 2 (shapes E, A, Bm, F#m): E, A are open. Score = 2
        chords = ["F#", "B", "C#m", "G#m"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 2)
        self.assertEqual(set(transposed_chords), set(["E", "A", "Bm", "F#m"]))

    def test_all_barre_chords_initially(self):
        # Sounding: F#m, Bm, C#m, Ebm (was G#m, Ebm is more distinct)
        # Capo 0: F#m, Bm, C#m, Ebm (0 open)
        # Capo 1 (shapes Fm, Bbm, Cm, Dm): Dm is open. Score = 3
        # Capo 2 (shapes Em, Am, Bm, Dbm): Em, Am are open. Score = 2
        # Capo 4 (shapes Dm, Gm, Am, Cbm=Bm): Dm, Am, Em (if Gm becomes Em) are open.
        #   F#m(-4) -> Dm. Bm(-4) -> Gm. C#m(-4) -> Am. Ebm(-4) -> Bbm.
        #   Shapes: Dm, Gm, Am, Bbm. Open: Dm, Am. Score = 2.
        # Capo 5 (shapes Cm, F#m, G#m, Am): Am is open. Score = 3
        chords = ["F#m", "Bm", "C#m", "Ebm"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        # Expected: Capo 2 (Shapes: Em, Am, Bm, Dbm/C#m) -> Em, Am are open. Score = 2
        # Or Capo 4 (Shapes: Dm, Gm, Am, Bbm) -> Dm, Am are open. Score = 2. Tie break to lower fret.
        self.assertEqual(fret, 2)
        self.assertEqual(set(transposed_chords), set(["Em", "Am", "Bm", "C#m"])) # music21 might give C#m for Dbm

    def test_empty_list(self):
        fret, transposed_chords = capo_advisor.recommend_capo([])
        self.assertEqual(fret, 0)
        self.assertEqual(transposed_chords, [])

    def test_unparseable_chord_skips_fret(self):
        # If a chord is unparseable for a capo position, that position should be skipped
        # and not become the "best" unless it's the only one or default.
        # ["C", "Xyz", "G"]
        # Capo 0: C, Xyz, G. If Xyz fails, this fret calculation might be skipped.
        # If all frets with Xyz fail, it should default to fret 0 and original chords.
        # The current logic breaks from the inner loop, so that fret's score isn't updated.
        # If all frets fail to parse all chords, best_fret remains 0, best_transposed remains original.
        chords = ["C", "Xyz", "G"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 0) # Defaults to 0 if all capo positions with Xyz fail
        self.assertEqual(transposed_chords, ["C", "Xyz", "G"])

    def test_prefer_lower_fret_on_tie(self):
        # Example: ["E", "A", "B"] (all open with Capo 0, Score 0)
        # Capo 0: E, A, B (Score 0)
        # If another capo position also yields Score 0, Capo 0 should be preferred.
        # Consider ["F#m", "Bm", "C#m"]
        # Capo 0: F#m, Bm, C#m (Score 3, 0 open)
        # Capo 2: Em, Am, Bm (Score 1, Em, Am open)
        # Capo 4: Dm, Gm, Am (Score 1, Dm, Am open)
        # Capo 2 and 4 have score 1. Lower fret (2) should be chosen.
        chords = ["F#m", "Bm", "C#m"]
        fret, transposed_chords = capo_advisor.recommend_capo(chords)
        self.assertEqual(fret, 2)
        self.assertEqual(set(transposed_chords), set(["Em", "Am", "Bm"]))


if __name__ == '__main__':
    unittest.main()
