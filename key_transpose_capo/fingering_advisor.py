import logging
import re
from typing import List, Optional, Tuple 

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
    min_fret_used = float('inf')
    max_fret_used = 0
    open_strings_count = 0
    muted_strings_count = 0
    fret_span = 0
    active_fingers = set() 

    for _string_idx, fret, finger in shape.fingerings:
        if finger > 0:
            active_fingers.add(finger) 
            if fret != 0: 
                min_fret_used = min(min_fret_used, fret)
                max_fret_used = max(max_fret_used, fret)
        elif finger == 0:
            open_strings_count += 1
        elif finger == -1:
            muted_strings_count += 1
    
    num_fingers_used = len(active_fingers) 

    if num_fingers_used > MIN_FINGERS_FOR_PENALTY:
        finger_penalty = (num_fingers_used - MIN_FINGERS_FOR_PENALTY) * WEIGHT_FINGER_COUNT
        score += finger_penalty

    if num_fingers_used > 0 and max_fret_used > 0 and min_fret_used != float('inf'): 
        fret_span = max_fret_used - min_fret_used
        if fret_span < 0: fret_span = 0 
    else: 
        fret_span = 0 
    
    if fret_span > 0 : 
        span_penalty = fret_span * WEIGHT_FRET_SPAN
        score += span_penalty

    open_bonus = open_strings_count * WEIGHT_OPEN_STRINGS
    score += open_bonus
    
    muted_penalty = muted_strings_count * WEIGHT_MUTED_STRINGS
    score += muted_penalty

    if shape.barre_strings_offset and shape.base_fret_of_template > 0:
        score += WEIGHT_BARRE
        if shape.barre_strings_offset: 
             barre_len_penalty = len(shape.barre_strings_offset)
             score += barre_len_penalty
    
    log.debug(
        f"Shape: {shape.name}, Final Score: {score} (Fingers: {num_fingers_used}, "
        f"Span: {fret_span}, Open: {open_strings_count}, Muted: {muted_strings_count}, "
        f"Barre: {bool(shape.barre_strings_offset and shape.base_fret_of_template > 0)})"
    )
    return score


def suggest_fingerings(
    chord_str: str,
    fretboard: Optional[Fretboard] = None
) -> List[ChordShape]:
    log.info(f"Suggesting fingerings for chord: {chord_str}")
    if fretboard is None:
        fretboard = Fretboard()

    root_match = re.match(r"([A-G][#b]?)", chord_str)
    if not root_match:
        log.error(f"Completely unparseable chord_str (no root): {chord_str}")
        return []
    actual_root_note_str = root_match.group(1)
    actual_root_value = music_theory_utils.get_note_value(actual_root_note_str)
    if actual_root_value is None: 
        log.error(f"Could not get value for regex-parsed root: {actual_root_note_str}")
        return []

    parsed_notes_list = music_theory_utils.parse_chord_to_notes(chord_str)
    
    if not parsed_notes_list or (len(parsed_notes_list) == 1 and parsed_notes_list[0] == chord_str):
        log.warning(f"Robust parsing failed for {chord_str}. Using simple quality from string.")
        quality_str_from_input = chord_str[len(actual_root_note_str):].strip()
        chord_type = quality_str_from_input.lower() if quality_str_from_input else "maj"
        if chord_type in ["m", "minor", "mi"]: chord_type = "min"
        elif chord_type == "": chord_type = "maj" 
    else:
        note_values = [music_theory_utils.get_note_value(n) for n in parsed_notes_list if n]
        valid_note_values = [nv for nv in note_values if nv is not None]
        chord_type = music_theory_utils.get_chord_type_from_intervals(actual_root_value, valid_note_values)
        
        if chord_type is None:
            quality_str_from_original = chord_str[len(actual_root_note_str):].strip() 
            chord_type = quality_str_from_original if quality_str_from_original else "maj"
            log.warning(f"Could not determine chord type from intervals for {chord_str} (root {actual_root_note_str}). Using fallback type '{chord_type}'.")

    root_note_str_for_shapes = actual_root_note_str 

    log.debug(f"Using Root='{root_note_str_for_shapes}', Type='{chord_type}' for shape lookup.")
    candidate_shapes = get_shapes_for_chord(root_note_str_for_shapes, chord_type) # Use root_note_str_for_shapes
    
    if not candidate_shapes:
        normalized_chord_type_fallback = chord_type.lower()
        if "maj" in normalized_chord_type_fallback and normalized_chord_type_fallback != "maj":
             log.debug(f"No shapes for '{chord_type}', trying 'maj' fallback for {root_note_str_for_shapes}")
             candidate_shapes = get_shapes_for_chord(root_note_str_for_shapes, "maj")
        elif ("min" in normalized_chord_type_fallback or "m" == normalized_chord_type_fallback) and \
             normalized_chord_type_fallback not in ["min", "m"]:
             log.debug(f"No shapes for '{chord_type}', trying 'min' fallback for {root_note_str_for_shapes}")
             candidate_shapes = get_shapes_for_chord(root_note_str_for_shapes, "min")

        if not candidate_shapes and ("maj" in chord_type or not chord_type): 
            candidate_shapes = get_shapes_for_chord(root_note_str_for_shapes, "maj")
        elif not candidate_shapes and ("min" in chord_type or "m" == chord_type): 
            candidate_shapes = get_shapes_for_chord(root_note_str_for_shapes, "min")

        if candidate_shapes:
            log.debug(f"Used fallback to basic major/minor shapes for {root_note_str_for_shapes}, original type '{chord_type}'.")

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
    fretboard_instance = Fretboard() 
    chords_to_test = ["C", "Gmaj", "Am", "Emin", "D7", "F#maj", "Bb", "Cmaj7", "Gm7", "F", "Bm"]
    for chord_test_str in chords_to_test:
        print(f"\n--- Testing: {chord_test_str} ---")
        suggestions = suggest_fingerings(chord_test_str, fretboard=fretboard_instance)
        if suggestions:
            for i, shape_sugg in enumerate(suggestions):
                print(f"  Suggestion {i+1}: {shape_sugg.name}") 
                print(f"     Fingerings: {shape_sugg.fingerings}")
        else:
            print(f"  No suggestions found for {chord_test_str}")
