"""
Capo advisor: recommends capo fret based on chord complexity heuristics.
"""
from typing import List, Tuple

def recommend_capo(chords: List[str]) -> Tuple[int, List[str]]:
    """
    Recommend a capo fret and return the transposed chord set.

    Scores each fret (0-7) by number of open chords, picks the best.

    Args:
        chords (List[str]): List of chord names as strings.

    Returns:
        Tuple[int, List[str]]: (recommended fret, list of transposed chords)

    Notes:
        Open chords are defined as {"C", "D", "E", "G", "A", "Em", "Am", "Dm"}.
        The function prefers the fret with the most open chords after transposition.
    """
    from music21 import harmony # Use harmony.ChordSymbol for better parsing and figure output
    
    # Consider expanding open_chords if desired, e.g., with common open 7ths
    open_chords = {"C", "D", "E", "G", "A", "Em", "Am", "Dm", 
                   "Cmaj7", "Gmaj7", "Dmaj7", "Amaj7", "Emaj7", # Common open Maj7
                   "C7", "D7", "E7", "G7", "A7",             # Common open Dom7
                   "Dm7", "Em7", "Am7"}                       # Common open min7


    best_fret = 0
    # Initialize best_score to a high value (e.g., number of chords, assuming all non-open)
    # or handle the case of an empty chord list first.
    if not chords:
        return 0, []

    best_score = len(chords) + 1 # Max possible non-open chords + 1
    best_transposed_shapes = list(chords) # Default to original if no better capo found

    for fret_to_try_capo in range(0, 8): # Capo on fret 0 to 7
        current_transposed_shapes = []
        current_score = 0
        possible_to_transpose_all = True
        for original_chord_str in chords:
            try:
                cs = harmony.ChordSymbol(original_chord_str)
                # To find playable shapes with capo at fret_to_try_capo,
                # transpose the sounding chord DOWN by that many semitones.
                transposed_shape_cs = cs.transpose(-fret_to_try_capo)
                shape_name = transposed_shape_cs.figure # Use .figure for standard notation
                current_transposed_shapes.append(shape_name)
                if shape_name not in open_chords:
                    current_score += 1
            except Exception as e:
                # If a chord can't be parsed/transposed, this capo position is problematic.
                # Option 1: Skip this fret entirely.
                # Option 2: Penalize heavily or mark as invalid.
                # Current choice: Skip this fret by breaking and not updating best_score.
                # log.warning(f"Error processing chord '{original_chord_str}' for capo {fret_to_try_capo}: {e}")
                possible_to_transpose_all = False
                break # Move to next fret if any chord fails for this capo position
        
        if possible_to_transpose_all and current_score < best_score:
            best_score = current_score
            best_fret = fret_to_try_capo
            best_transposed_shapes = current_transposed_shapes
        elif possible_to_transpose_all and current_score == best_score:
            # Tie-breaking: prefer lower capo fret if scores are equal
            if fret_to_try_capo < best_fret:
                best_fret = fret_to_try_capo
                best_transposed_shapes = current_transposed_shapes
                
    return best_fret, best_transposed_shapes
