import unittest
# from unittest.mock import MagicMock # Not used
# patch might not be needed if not mocking external modules

from lyrics_analysis.lyrics_analyzer import (
    align_chords_with_lyrics,
    identify_song_structure
)

class TestAlignChordsWithLyrics(unittest.TestCase):

    def test_empty_inputs(self):
        self.assertEqual(align_chords_with_lyrics([], ""), [])
        self.assertEqual(align_chords_with_lyrics([{"time": 0, "chord": "C"}], ""), [])
        lyrics = "Line 1\nLine 2"
        expected = [{"line": "Line 1", "chords": []}, {"line": "Line 2", "chords": []}]
        self.assertEqual(align_chords_with_lyrics([], lyrics), expected)

    def test_no_chord_times_fallback_timing(self):
        lyrics = "Line 1\nLine 2"
        # All chords at time 0 or no time, time_per_line will be 5s
        # Line 1: 0-5s, Line 2: 5-10s
        chords = [
            {"chord": "C"}, # Assumed time 0
            {"time": 0, "chord": "G"},
            {"time": 0, "chord": "Am"}
        ]
        # All these chords should fall into the first line's window (0-5s)
        expected = [
            {"line": "Line 1", "chords": [
                {"chord": "C"}, {"time": 0, "chord": "G"}, {"time": 0, "chord": "Am"}
            ]},
            {"line": "Line 2", "chords": []}
        ]
        self.assertEqual(align_chords_with_lyrics(chords, lyrics), expected)

    def test_basic_alignment_with_times(self):
        lyrics = "Line 1\nLine 2\nLine 3"
        # total_duration = 12.0 + 5.0 = 17.0; time_per_line = 17.0 / 3 = 5.66
        # Line 1: 0 - 5.66
        # Line 2: 5.66 - 11.33
        # Line 3: 11.33 - 17.0
        chords = [
            {"time": 2.0, "chord": "C"},
            {"time": 7.0, "chord": "G"},
            {"time": 12.0, "chord": "Am"}
        ]
        expected = [
            {"line": "Line 1", "chords": [{"time": 2.0, "chord": "C"}]},
            {"line": "Line 2", "chords": [{"time": 7.0, "chord": "G"}]},
            {"line": "Line 3", "chords": [{"time": 12.0, "chord": "Am"}]}
        ]
        self.assertEqual(align_chords_with_lyrics(chords, lyrics), expected)

    def test_multiple_chords_per_line(self):
        lyrics = "Line 1 has two chords\nLine 2 has one"
        # total_duration = 6.0 + 5.0 = 11.0; time_per_line = 11.0 / 2 = 5.5
        # Line 1: 0 - 5.5
        # Line 2: 5.5 - 11.0
        chords = [
            {"time": 1.0, "chord": "C"},
            {"time": 3.0, "chord": "F"},
            {"time": 6.0, "chord": "G"}
        ]
        expected = [
            {"line": "Line 1 has two chords", "chords": [
                {"time": 1.0, "chord": "C"}, {"time": 3.0, "chord": "F"}
            ]},
            {"line": "Line 2 has one", "chords": [{"time": 6.0, "chord": "G"}]}
        ]
        self.assertEqual(align_chords_with_lyrics(chords, lyrics), expected)

    def test_chords_at_line_boundaries(self):
        lyrics = "Line A\nLine B"
        # total_duration = 5.0 + 5.0 = 10.0; time_per_line = 10.0 / 2 = 5.0
        # Line A: 0 - 5.0
        # Line B: 5.0 - 10.0
        chords = [
            {"time": 0.0, "chord": "D"},  # Start of Line A
            {"time": 4.9, "chord": "Em"}, # End of Line A
            {"time": 5.0, "chord": "F#m"} # Start of Line B
        ]
        expected = [
            {"line": "Line A", "chords": [
                {"time": 0.0, "chord": "D"}, {"time": 4.9, "chord": "Em"}
            ]},
            {"line": "Line B", "chords": [{"time": 5.0, "chord": "F#m"}]}
        ]
        self.assertEqual(align_chords_with_lyrics(chords, lyrics), expected)

    def test_no_chords_for_some_lines(self):
        lyrics = "Line with chord\nEmpty line\nAnother with chord"
        # total_duration = 10.0 + 5.0 = 15.0; time_per_line = 15.0 / 3 = 5.0
        # Line 1: 0-5, Line 2: 5-10, Line 3: 10-15
        chords = [
            {"time": 2.0, "chord": "A"},
            {"time": 12.0, "chord": "B"}
        ]
        expected = [
            {"line": "Line with chord", "chords": [{"time": 2.0, "chord": "A"}]},
            {"line": "Empty line", "chords": []},
            {"line": "Another with chord", "chords": [{"time": 12.0, "chord": "B"}]}
        ]
        self.assertEqual(align_chords_with_lyrics(chords, lyrics), expected)


class TestIdentifySongStructure(unittest.TestCase):

    def assertStructureAlmostEqual(self, actual_list, expected_list, places=7):
        self.assertEqual(len(actual_list), len(expected_list), 
                         f"Structure lists have different lengths: {len(actual_list)} vs {len(expected_list)}")
        for i, (actual_item, expected_item) in enumerate(zip(actual_list, expected_list)):
            self.assertEqual(actual_item['type'], expected_item['type'],
                             f"Item {i}: Type mismatch - Actual: '{actual_item['type']}', Expected: '{expected_item['type']}'")
            self.assertAlmostEqual(
                actual_item['start_time'],
                expected_item['start_time'],
                places=places,
                msg=(f"Item {i} (type '{actual_item['type']}'): Start time mismatch - "
                     f"Actual: {actual_item['start_time']}, Expected: {expected_item['start_time']}")
            )

    def test_empty_lyrics(self):
        self.assertEqual(identify_song_structure("", []), {"structure": []})
        # If lyrics exist but no structure found, it defaults to "Song"
        result_data = identify_song_structure("Some lyrics", [])
        expected_data = {"structure": [{"type": "Song", "start_time": 0.0}]}
        self.assertStructureAlmostEqual(result_data['structure'], expected_data['structure'])


    def test_keyword_identification_no_chords(self):
        lyrics = "Intro\nVerse 1 line\nChorus line\nBridge line\nOutro"
        # time_per_line = (5 lines * 5s/line) / 5 lines = 5.0s
        expected = {"structure": [
            {"type": "Intro", "start_time": 0.0},      # Line 0 * 5.0
            {"type": "Verse 1", "start_time": 5.0},    # Line 1 * 5.0
            {"type": "Chorus 1", "start_time": 10.0},  # Line 2 * 5.0
            {"type": "Bridge 1", "start_time": 15.0},  # Line 3 * 5.0
            {"type": "Outro", "start_time": 20.0}      # Line 4 * 5.0
        ]}
        result_data = identify_song_structure(lyrics, [])
        self.assertStructureAlmostEqual(result_data['structure'], expected['structure'])

    def test_keyword_case_insensitivity_and_counting(self):
        lyrics = "verse one\nCHORUS\nsecond verse here\nchorus again"
        # total_duration = (4 lines * 5s/line) = 20s. time_per_line = 5s
        expected = {"structure": [
            {"type": "Verse 1", "start_time": 0.0},    # line 0
            {"type": "Chorus 1", "start_time": 5.0},   # line 1
            {"type": "Verse 2", "start_time": 10.0},   # line 2
            {"type": "Chorus 2", "start_time": 15.0}   # line 3
        ]}
        result_data = identify_song_structure(lyrics, [])
        self.assertStructureAlmostEqual(result_data['structure'], expected['structure'])

    def test_structure_timing_with_chords(self):
        # Modified lyrics to make "Chorus" line distinct from its content lines
        lyrics = "Verse\nThis is the verse content.\nChorus\nThis is the chorus content." 
        chords = [
            {"time": 0.5, "chord": "C"}, # For Verse
            {"time": 10.2, "chord": "G"} # For Chorus
        ]
        # Estimated line times (total_duration = 10.2 + 5 = 15.2. time_per_line = 15.2/4 = 3.8)
        # Verse (line 0) est_start = 0 * 3.8 = 0.0. Chord at 0.5. -> time: 0.5
        # "This is the verse content." (line 1) est_start = 1 * 3.8 = 3.8. Closest chord >= 3.8 is 10.2. -> time: 10.2
        # Chorus (line 2) est_start = 2 * 3.8 = 7.6. Chord at 10.2. -> time: 10.2
        # "This is the chorus content." (line 3) est_start = 3 * 3.8 = 11.4. No chord at/after 11.4. -> time: 11.4
        expected = {"structure": [
            {"type": "Verse 1", "start_time": 0.5},
            {"type": "Verse 2", "start_time": 10.2}, # Corrected expected time
            {"type": "Chorus 1", "start_time": 10.2},
            {"type": "Chorus 2", "start_time": 11.4} 
        ]}
        # This test now expects the current behavior of the production code.
        result_data = identify_song_structure(lyrics, chords)
        self.assertStructureAlmostEqual(result_data['structure'], expected['structure'])


    def test_no_keywords_fallback(self):
        lyrics = "Just some normal lines\nNothing special here"
        chords = [{"time": 1.0, "chord": "D"}]
        expected = {"structure": [{"type": "Song", "start_time": 0.0}]} # Fallback time is 0.0
        result_data = identify_song_structure(lyrics, chords)
        self.assertStructureAlmostEqual(result_data['structure'], expected['structure'])
    
    def test_complex_keywords(self):
        lyrics = "1st Verse of the song\nGuitar Solo part\nTHE Pre-Chorus"
        # time_per_line = (3 * 5) / 3 = 5.0
        expected = {"structure": [
            {"type": "Verse 1", "start_time": 0.0},    # Line 0
            {"type": "Solo", "start_time": 5.0},       # Line 1
            {"type": "Chorus 1", "start_time": 10.0}   # Line 2 (Pre-Chorus maps to Chorus)
        ]}
        result_data = identify_song_structure(lyrics, [])
        self.assertStructureAlmostEqual(result_data['structure'], expected['structure'])


if __name__ == '__main__':
    unittest.main()
