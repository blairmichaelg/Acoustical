import logging
import re # Added re import
from typing import List, Dict, Any, Optional, Tuple

from music_theory import utils as music_theory_utils
from music_theory.fretboard import Fretboard
from music_theory.chord_shapes import ChordShape, get_shapes_for_chord

log = logging.getLogger(__name__)

# Heuristic scoring weights (can be tuned)
WEIGHT_OPEN_STRINGS = -5  # Bonus for open strings
WEIGHT_BARRE = 20         # Penalty for barre
WEIGHT_FINGER_COUNT = 2   # Penalty per finger used (beyond a minimum)
WEIGHT_FRET_SPAN = 3      # Penalty for large fret span
WEIGHT_MUTED_STRINGS = 1  # Penalty per muted string

MIN_FINGERS_FOR_PENALTY = 2  # Only penalize finger count above this

# class FingeringSuggestion(ChordShape): # Not used as a separate class for now
#     """
#     Extends ChordShape to include a playability score.
#     """
#     score: int


def score_shape_playability(shape: ChordShape, fretboard: Fretboard) -> int:
    """
    Calculates a playability score for a given chord shape.
    Lower score is better (easier to play).
    """
    score = 0
    num_fingers_used = 0
    min_fret_used = float('inf')
    max_fret_used = 0
    open_strings_count = 0
    muted_strings_count = 0
    fret_span = 0 # Initialize fret_span

    for _string_idx, fret, finger in shape.fingerings:
        if finger > 0:  # Actual finger used
            num_fingers_used += 1
            if fret != 0:  # Don't count open strings for fret span
                min_fret_used = min(min_fret_used, fret)
                max_fret_used = max(max_fret_used, fret)
        elif finger == 0:  # Open string
            open_strings_count += 1
        elif finger == -1:  # Muted string
            muted_strings_count += 1

    # Penalty for finger count
    if num_fingers_used > MIN_FINGERS_FOR_PENALTY:
        score += (num_fingers_used - MIN_FINGERS_FOR_PENALTY) * WEIGHT_FINGER_COUNT

    # Penalty for fret span
    if num_fingers_used > 0 and max_fret_used > 0:
        fret_span = max_fret_used - min_fret_used if min_fret_used != float('inf') else 0
        score += fret_span * WEIGHT_FRET_SPAN

    # Bonus for open strings
    score += open_strings_count * WEIGHT_OPEN_STRINGS  # Negative weight is a bonus

    # Penalty for muted strings
    score += muted_strings_count * WEIGHT_MUTED_STRINGS

    # Penalty for barre chords
    if shape.barre_strings and shape.base_fret > 0:  # base_fret > 0 implies it's a barre
        score += WEIGHT_BARRE
        score += len(shape.barre_strings)  # Small penalty per string barred

    log.debug(
        f"Shape: {shape.name}, Score: {score} (Fingers: {num_fingers_used}, "
        f"Span: {fret_span}, Open: {open_strings_count}, Muted: {muted_strings_count}, "
        f"Barre: {bool(shape.barre_strings and shape.base_fret > 0)})"
    )
    return score


def suggest_fingerings(
    chord_str: str,
    fretboard: Optional[Fretboard] = None,
    context: Optional[Dict[str, Any]] = None  # For future use
) -> List[ChordShape]:
    """
    Suggests guitar fingerings for a given chord string.

    Args:
        chord_str (str): The chord to find fingerings for (e.g., "Cmaj7", "Gsus4").
        fretboard (Optional[Fretboard]): An initialized Fretboard object.
                                         If None, a default one will be created.
        context (Optional[Dict[str, Any]]): Additional context.

    Returns:
        List[ChordShape]: Sorted list of ChordShape objects (easiest first).
    """
    log.info(f"Suggesting fingerings for chord: {chord_str}")
    if fretboard is None:
        fretboard = Fretboard()  # Default fretboard

    root_match = re.match(r"([A-G][#b]?)", chord_str)
    if not root_match:
        log.warning(f"Could not parse root from chord_str: {chord_str}")
        return []

    root_note_str = root_match.group(1)
    quality_str = chord_str[len(root_note_str):]

    # Normalize quality_str
    chord_type = quality_str.lower()
    if not quality_str or chord_type == "major":
        chord_type = "maj"
    elif chord_type in ["m", "minor", "mi"]:
        chord_type = "min"
    elif chord_type in ["7", "dominant7", "dom7"]: # Default to dominant 7th for "7"
        chord_type = "7"
    # TODO: Add more normalizations for maj7, m7, dim, aug etc.
    # For now, if not explicitly normalized, use the (lower-cased) quality_str
    # This relies on COMMON_CHORD_SHAPES having keys like "maj7", "m7" etc.
    # or the get_shapes_for_chord function handling it.

    log.debug(f"Parsed chord: Root='{root_note_str}', Type='{chord_type}' (from '{quality_str}')")

    candidate_shapes = get_shapes_for_chord(root_note_str, chord_type)

    # TODO: Implement transposition for movable shapes

    scored_shapes: List[Tuple[ChordShape, int]] = []
    for shape in candidate_shapes:
        score = score_shape_playability(shape, fretboard)
        scored_shapes.append((shape, score))

    scored_shapes.sort(key=lambda item: item[1])

    final_suggestions = [shape for shape, score in scored_shapes]

    if not final_suggestions:
        log.info(f"No fingerings found for {chord_str} with current library/logic.")
    elif scored_shapes: # Check if scored_shapes is not empty
        log.info(
            f"Found {len(final_suggestions)} fingerings for {chord_str}, "
            f"best score: {scored_shapes[0][1]}"
        )

    return final_suggestions


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # 're' is already imported at the top of the file.

    fb = Fretboard()

    chords_to_test = ["C", "G", "Am", "E", "D7", "F#"]  # F# will be empty

    for chord_test_str in chords_to_test:
        print(f"\n--- Testing: {chord_test_str} ---")
        suggestions = suggest_fingerings(chord_test_str, fretboard=fb)
        if suggestions:
            for i, shape_sugg in enumerate(suggestions):
                score_display = score_shape_playability(shape_sugg, fb)
                print(f"  Suggestion {i+1}: {shape_sugg.name} (Score: {score_display})")
                print(f"     Fingerings: {shape_sugg.fingerings}")
        else:
            print(f"  No suggestions found for {chord_test_str}")
