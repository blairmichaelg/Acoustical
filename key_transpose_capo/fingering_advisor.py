import logging
import re
from typing import List, Dict, Any, Optional, Tuple

from music_theory import utils as music_theory_utils
from music_theory.fretboard import Fretboard
from music_theory.chord_shapes import ChordShape, get_shapes_for_chord

log = logging.getLogger(__name__)

# Heuristic scoring weights
WEIGHT_OPEN_STRINGS = -5
WEIGHT_BARRE = 20
WEIGHT_FINGER_COUNT = 2
WEIGHT_FRET_SPAN = 3
WEIGHT_MUTED_STRINGS = 1
MIN_FINGERS_FOR_PENALTY = 2


def score_shape_playability(shape: ChordShape, fretboard: Fretboard) -> int:
    score = 0
    num_fingers_used = 0
    min_fret_used = float('inf')
    max_fret_used = 0
    open_strings_count = 0
    muted_strings_count = 0
    fret_span = 0

    for _string_idx, fret, finger in shape.fingerings:
        if finger > 0:
            num_fingers_used += 1
            if fret != 0:
                min_fret_used = min(min_fret_used, fret)
                max_fret_used = max(max_fret_used, fret)
        elif finger == 0:
            open_strings_count += 1
        elif finger == -1:
            muted_strings_count += 1

    if num_fingers_used > MIN_FINGERS_FOR_PENALTY:
        score += (num_fingers_used - MIN_FINGERS_FOR_PENALTY) * WEIGHT_FINGER_COUNT

    if num_fingers_used > 0 and max_fret_used > 0:
        fret_span = max_fret_used - min_fret_used if min_fret_used != float('inf') else 0
        score += fret_span * WEIGHT_FRET_SPAN

    score += open_strings_count * WEIGHT_OPEN_STRINGS
    score += muted_strings_count * WEIGHT_MUTED_STRINGS

    if shape.barre_strings_offset and shape.base_fret_of_template > 0: # Check template base fret for barre
        # The actual barre fret is template.base_fret_of_template + transposition_offset
        # For scoring, we care if the *resulting* shape is a barre.
        # This logic might need refinement if base_fret_of_template is not the actual barre fret
        # but rather the fret of the *transposed* shape.
        # Let's assume shape.base_fret_of_template refers to the final barre fret of the shape.
        # The `_transpose_shape` sets `base_fret_of_template` to the new barre fret.
        score += WEIGHT_BARRE
        if shape.barre_strings_offset: # Check again, as it's Optional
             score += len(shape.barre_strings_offset)


    log.debug(
        f"Shape: {shape.name}, Score: {score} (Fingers: {num_fingers_used}, "
        f"Span: {fret_span}, Open: {open_strings_count}, Muted: {muted_strings_count}, "
        f"Barre: {bool(shape.barre_strings_offset and shape.base_fret_of_template > 0)})"
    )
    return score


def suggest_fingerings(
    chord_str: str,
    fretboard: Optional[Fretboard] = None,
    context: Optional[Dict[str, Any]] = None
) -> List[ChordShape]:
    log.info(f"Suggesting fingerings for chord: {chord_str}")
    if fretboard is None:
        fretboard = Fretboard()

    parsed_notes_str = music_theory_utils.parse_chord_to_notes(chord_str)
    if not parsed_notes_str or parsed_notes_str[0] == chord_str: # Parsing failed
        log.warning(f"Could not robustly parse chord: {chord_str}. Attempting simple match.")
        # Fallback to regex for root and simple quality if robust parsing fails
        root_match = re.match(r"([A-G][#b]?)", chord_str)
        if not root_match:
            log.error(f"Completely unparseable chord_str: {chord_str}")
            return []
        root_note_str = root_match.group(1)
        quality_str = chord_str[len(root_note_str):]
        chord_type = quality_str.lower() if quality_str else "maj"
        if chord_type in ["m", "minor", "mi"]: chord_type = "min"
        elif chord_type in ["7", "dominant7", "dom7"]: chord_type = "7"
        # This fallback is limited
    else:
        root_note_str = parsed_notes_str[0]
        root_value = music_theory_utils.get_note_value(root_note_str)
        if root_value is None: # Should not happen if parse_chord_to_notes worked
            log.error(f"Could not get root value for parsed root: {root_note_str}")
            return []
            
        note_values = [music_theory_utils.get_note_value(n) for n in parsed_notes_str]
        # Filter out None values if any note parsing failed within parse_chord_to_notes
        valid_note_values = [nv for nv in note_values if nv is not None]
        
        chord_type = music_theory_utils.get_chord_type_from_intervals(root_value, valid_note_values)
        if chord_type is None:
            # Fallback if type determination fails, try to use raw quality string
            # Ensure root_note_str is available here from the current scope
            quality_str_from_original = chord_str[len(root_note_str):].strip() 
            chord_type = quality_str_from_original if quality_str_from_original else "maj"
            log.warning(f"Could not determine chord type from intervals for {chord_str}. Using '{chord_type}'.")


    log.debug(f"Using Root='{root_note_str}', Type='{chord_type}' for shape lookup.")
    candidate_shapes = get_shapes_for_chord(root_note_str, chord_type)
    
    # If no shapes found with specific type, try with just "maj" or "min" if applicable
    if not candidate_shapes:
        if "maj" in chord_type:
            candidate_shapes = get_shapes_for_chord(root_note_str, "maj")
        elif "min" in chord_type or "m" == chord_type : # m without 7,9 etc.
            candidate_shapes = get_shapes_for_chord(root_note_str, "min")
        if candidate_shapes:
            log.debug(f"Falling back to basic major/minor shapes for {root_note_str}{chord_type}")


    scored_shapes: List[Tuple[ChordShape, int]] = []
    for shape in candidate_shapes:
        score = score_shape_playability(shape, fretboard)
        scored_shapes.append((shape, score))

    scored_shapes.sort(key=lambda item: item[1])
    final_suggestions = [shape for shape, score in scored_shapes]

    if not final_suggestions:
        log.info(f"No fingerings found for {chord_str}.")
    elif scored_shapes:
        log.info(
            f"Found {len(final_suggestions)} fingerings for {chord_str}, "
            f"best score: {scored_shapes[0][1]}"
        )
    return final_suggestions


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fretboard_instance = Fretboard() # Use a different variable name
    chords_to_test = ["C", "Gmaj", "Am", "Emin", "D7", "F#maj", "Bb", "Cmaj7", "Gm7"]
    for chord_test_str in chords_to_test:
        print(f"\n--- Testing: {chord_test_str} ---")
        suggestions = suggest_fingerings(chord_test_str, fretboard=fretboard_instance)
        if suggestions:
            for i, shape_sugg in enumerate(suggestions):
                score_display = score_shape_playability(shape_sugg, fretboard_instance) 
                print(f"  Suggestion {i+1}: {shape_sugg.name} (Score: {score_display})")
                print(f"     Fingerings: {shape_sugg.fingerings}")
        else:
            print(f"  No suggestions found for {chord_test_str}")
