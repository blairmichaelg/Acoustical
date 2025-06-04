import logging
import re
from typing import List, Dict, Optional

log = logging.getLogger(__name__)

NOTES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

NOTE_TO_VALUE: Dict[str, int] = {note: i for i, note in enumerate(NOTES_SHARP)}
NOTE_TO_VALUE.update({note: i for i, note in enumerate(NOTES_FLAT)})  # Add flat equivalents

VALUE_TO_NOTE_SHARP: Dict[int, str] = {i: note for i, note in enumerate(NOTES_SHARP)}
VALUE_TO_NOTE_FLAT: Dict[int, str] = {i: note for i, note in enumerate(NOTES_FLAT)}

INTERVALS: Dict[str, int] = {
    "P1": 0, "unison": 0,
    "m2": 1, "min2": 1,
    "M2": 2, "maj2": 2,
    "m3": 3, "min3": 3,
    "M3": 4, "maj3": 4,
    "P4": 5, "perf4": 5,
    "A4": 6, "aug4": 6, "d5": 6, "dim5": 6,  # Tritone
    "P5": 7, "perf5": 7,
    "m6": 8, "min6": 8, "A5": 8, "aug5": 8,
    "M6": 9, "maj6": 9, "d7": 9, "dim7_interval": 9,  # Diminished 7th interval (enharmonically M6)
    "m7": 10, "min7_interval": 10,  # Minor 7th interval
    "M7": 11, "maj7_interval": 11,  # Major 7th interval
    "P8": 12, "octave": 12
}
VALUE_TO_INTERVAL_NAME: Dict[int, str] = {
    0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
    6: "A4/d5", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7"
}

CHORD_FORMULAS: Dict[str, List[int]] = {
    "maj": [0, 4, 7],
    "m": [0, 3, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "sus4": [0, 5, 7],
    "sus2": [0, 2, 7],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "M7": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10],
    "min7": [0, 3, 7, 10],
    "m7b5": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9],
    "6": [0, 4, 7, 9],
    "m6": [0, 3, 7, 9],
    "9": [0, 4, 7, 10, 2 + 12],
    "maj9": [0, 4, 7, 11, 2 + 12],
    "m9": [0, 3, 7, 10, 2 + 12],
    "add9": [0, 4, 7, 2 + 12],
    "madd9": [0, 3, 7, 2 + 12],
}

CHORD_QUALITY_PATTERNS = [
    (re.compile(r"m7b5$"), "m7b5"), (re.compile(r"maj9$"), "maj9"),
    (re.compile(r"m9$"), "m9"), (re.compile(r"add9$"), "add9"),
    (re.compile(r"madd9$"), "madd9"), (re.compile(r"9$"), "9"),
    (re.compile(r"maj7$"), "maj7"), (re.compile(r"M7$"), "M7"),
    (re.compile(r"m7$"), "m7"), (re.compile(r"min7$"), "min7"),
    (re.compile(r"dim7$"), "dim7"), (re.compile(r"7$"), "7"),
    (re.compile(r"m6$"), "m6"), (re.compile(r"6$"), "6"),
    (re.compile(r"sus4$"), "sus4"), (re.compile(r"sus2$"), "sus2"),
    (re.compile(r"dim$"), "dim"), (re.compile(r"aug$"), "aug"),
    (re.compile(r"m$"), "m"), (re.compile(r"min$"), "min"),
    (re.compile(r"maj$"), "maj"), (re.compile(r"$"), "maj"),
]

SCALE_PATTERNS: Dict[str, List[int]] = {
    "major": [0,2,4,5,7,9,11], "minor": [0,2,3,5,7,8,10],
    "harmonic_minor": [0,2,3,5,7,8,11], "melodic_minor": [0,2,3,5,7,9,11],
    "dorian": [0,2,3,5,7,9,10], "phrygian": [0,1,3,5,7,8,10],
    "lydian": [0,2,4,6,7,9,11], "mixolydian": [0,2,4,5,7,9,10],
    "locrian": [0,1,3,5,6,8,10], "pentatonic_major": [0,2,4,7,9],
    "pentatonic_minor": [0,3,5,7,10], "blues": [0,3,5,6,7,10]
}

def get_note_value(note_str: str) -> Optional[int]:
    if not isinstance(note_str, str):
        log.warning(f"Invalid input type for note_str: {type(note_str)}. Expected string.")
        return None
    note_str_processed = note_str.strip().capitalize().replace("H", "B")
    match = re.match(r"([A-G][#b]?)", note_str_processed)
    if not match:
        log.warning(f"Could not extract valid note name from: {note_str}")
        return None
    core_note_name = match.group(1)
    val = NOTE_TO_VALUE.get(core_note_name)
    if val is None:
        log.warning(f"Could not parse core note name: {core_note_name} from original: {note_str}")
    return val

def get_note_name(note_value: int, prefer_sharp: bool = True) -> str:
    note_value %= 12
    return (VALUE_TO_NOTE_SHARP if prefer_sharp else VALUE_TO_NOTE_FLAT).get(note_value, "N/A")

def parse_chord_to_notes(chord_string: str, prefer_sharp_for_output: bool = True) -> List[str]:
    log.info(f"Parsing chord: {chord_string}")
    original_chord_string = chord_string
    processed_chord_string = chord_string.replace("H", "B")
    root_match = re.match(r"([A-G][#b]?)", processed_chord_string)
    if not root_match:
        log.warning(f"Could not parse root note from: {original_chord_string}")
        return [original_chord_string]
    root_note_str = root_match.group(1)
    root_value = get_note_value(root_note_str)
    if root_value is None: return [original_chord_string]
    quality_str = processed_chord_string[len(root_note_str):].strip()
    formula_key_to_use = next((k for pat, k in CHORD_QUALITY_PATTERNS if pat.fullmatch(quality_str)), None)
    if not formula_key_to_use and not quality_str: formula_key_to_use = "maj"
    intervals = CHORD_FORMULAS.get(formula_key_to_use) if formula_key_to_use else None
    if intervals is None:
        log.warning(f"Unknown quality '{quality_str}' in '{original_chord_string}'. Returning root.")
        return [get_note_name(root_value, prefer_sharp_for_output)]
    chord_note_values = sorted(list(set((root_value + i) % 12 for i in intervals)))
    final_prefer_sharp = prefer_sharp_for_output
    if (len(root_note_str) > 1 and root_note_str[1] == 'b') or root_note_str == "F":
        final_prefer_sharp = False
    if root_note_str in ["C", "G"] and formula_key_to_use == "maj":
        final_prefer_sharp = True
    chord_notes = [get_note_name(v, final_prefer_sharp) for v in chord_note_values]
    log.debug(f"Parsed '{original_chord_string}' to {chord_notes}")
    # print(f"DEBUG parse_chord_to_notes: input='{original_chord_string}', output_notes={chord_notes}, root_value={root_value}, quality_str='{quality_str}', formula_key='{formula_key_to_use}'") # DEBUG
    return chord_notes

def get_chord_type_from_intervals(root_value: int, note_values: List[int]) -> Optional[str]:
    if not note_values or root_value is None: return None
    intervals_from_root = sorted(list(set((val - root_value + 12) % 12 for val in note_values)))
    if 0 not in intervals_from_root : intervals_from_root.insert(0,0)
    # print(f"DEBUG get_chord_type_from_intervals: root_value={root_value}, note_values={note_values}, intervals_from_root={intervals_from_root}")

    # Sort CHORD_FORMULAS by length of interval list (descending) to check more specific chords first
    # Then by key name for consistent tie-breaking if lengths are equal.
    sorted_formulas = sorted(CHORD_FORMULAS.items(), key=lambda item: (len(item[1]), item[0]), reverse=True)

    for type_name, formula_intervals in sorted_formulas:
        # Ensure formula_intervals are also sorted for consistent comparison if needed, though set comparison handles order.
        if set(intervals_from_root) == set(formula_intervals):
            # Return the exact type_name from CHORD_FORMULAS.
            # Downstream functions will handle any necessary normalization.
            # print(f"DEBUG get_chord_type_from_intervals: Matched sorted_formulas: {type_name} for intervals {intervals_from_root}") # Reverted print
            return type_name
    
    # Explicit fallback for basic major/minor if not caught by sorted list
    # print(f"DEBUG get_chord_type_from_intervals: Fallback check. intervals_from_root = {intervals_from_root} (type: {type(intervals_from_root)})")
    if intervals_from_root == [0, 4, 7]: # Direct list comparison for major triad
        # print("DEBUG get_chord_type_from_intervals: Matched explicit fallback direct: maj FOR [0,4,7]")
        return "maj"
    if intervals_from_root == [0, 3, 7]: # Direct list comparison for minor triad
        # print("DEBUG get_chord_type_from_intervals: Matched explicit fallback direct: min FOR [0,3,7]")
        return "min"
            
    log.warning(f"Could not determine chord type for intervals: {intervals_from_root} from root_value {root_value}")
    return None


def generate_scale(root_note_str: str, scale_type: str = "major") -> List[str]:
    log.info(f"Generating {root_note_str} {scale_type} scale")
    root_value = get_note_value(root_note_str)
    if root_value is None: return []
    pattern = SCALE_PATTERNS.get(scale_type.lower())
    if not pattern:
        log.warning(f"Unknown scale type: {scale_type}. Defaulting to major.")
        pattern = SCALE_PATTERNS["major"]
    scale_values = [(root_value + i) % 12 for i in pattern]
    prefer_flats = (len(root_note_str) > 1 and root_note_str[1] == 'b') or root_note_str == "F"
    scale_notes = [get_note_name(v, not prefer_flats) for v in scale_values]
    log.debug(f"Generated {scale_type} scale for {root_note_str}: {scale_notes}")
    return scale_notes

def calculate_interval(note1_str: str, note2_str: str) -> Optional[str]:
    val1, val2 = get_note_value(note1_str), get_note_value(note2_str)
    if val1 is None or val2 is None: return None
    interval_val = (val2 - val1 + 12) % 12
    name = VALUE_TO_INTERVAL_NAME.get(interval_val)
    log.info(f"Interval {note1_str}-{note2_str}: {name} ({interval_val} semitones)")
    return name
