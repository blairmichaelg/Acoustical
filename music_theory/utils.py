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
    "M6": 9, "maj6": 9, "d7": 9, "dim7_interval": 9,  # Diminished 7th interval
    "m7": 10, "min7_interval": 10,  # Minor 7th interval
    "M7": 11, "maj7_interval": 11,  # Major 7th interval
    "P8": 12, "octave": 12
}
VALUE_TO_INTERVAL_NAME: Dict[int, str] = {
    0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
    6: "A4/d5", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7"
}

# Chord formulas: semitones from root
CHORD_FORMULAS: Dict[str, List[int]] = {
    # Triads
    "maj": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"]],
    "m": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"]],
    "min": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"]],  # Alias
    "dim": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["d5"]],
    "aug": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["A5"]],
    "sus4": [INTERVALS["P1"], INTERVALS["P4"], INTERVALS["P5"]],
    "sus2": [INTERVALS["P1"], INTERVALS["M2"], INTERVALS["P5"]],
    # Sevenths
    "7": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"], INTERVALS["m7"]],
    "maj7": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"], INTERVALS["M7"]],
    "M7": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"], INTERVALS["M7"]],  # Alias
    "m7": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"], INTERVALS["m7"]],
    "min7": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"], INTERVALS["m7"]],  # Alias
    "m7b5": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["d5"], INTERVALS["m7"]],
    "dim7": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["d5"], INTERVALS["d7"]],
    # Sixths
    "6": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"], INTERVALS["M6"]],
    "m6": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"], INTERVALS["M6"]],
    # Ninths
    "9": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"],
          INTERVALS["m7"], INTERVALS["M2"] + 12],
    "maj9": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"],
             INTERVALS["M7"], INTERVALS["M2"] + 12],
    "m9": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"],
           INTERVALS["m7"], INTERVALS["M2"] + 12],
    # Add chords
    "add9": [INTERVALS["P1"], INTERVALS["M3"], INTERVALS["P5"],
             INTERVALS["M2"] + 12],
    "madd9": [INTERVALS["P1"], INTERVALS["m3"], INTERVALS["P5"],
              INTERVALS["M2"] + 12],
}


def get_note_value(note_str: str) -> Optional[int]:
    """Parses a note string and returns its numerical value (0-11)."""
    note_str_cleaned = note_str.strip().capitalize()
    if note_str_cleaned in NOTE_TO_VALUE:
        return NOTE_TO_VALUE[note_str_cleaned]
    log.warning(f"Could not parse note: {note_str}")
    return None


def get_note_name(note_value: int, prefer_sharp: bool = True) -> str:
    """Converts a numerical value back to a note name."""
    note_value = note_value % 12
    if prefer_sharp:
        return VALUE_TO_NOTE_SHARP.get(note_value, "N/A")
    else:
        return VALUE_TO_NOTE_FLAT.get(note_value, "N/A")


def parse_chord_to_notes(chord_string: str, prefer_sharp: bool = True) -> List[str]:
    """
    Parses a chord string into its constituent notes.
    """
    log.info(f"Parsing chord: {chord_string}")
    original_chord_string = chord_string  # Keep for logging

    match = re.match(r"([A-G][#b]?)", chord_string)
    if not match:
        log.warning(f"Could not parse root note from chord: {original_chord_string}")
        return [original_chord_string]

    root_note_str = match.group(1)
    root_value = get_note_value(root_note_str)
    if root_value is None:
        log.warning(f"Invalid root note in chord: {original_chord_string}")
        return [original_chord_string]

    quality_str = chord_string[len(root_note_str):].strip()
    if not quality_str:
        quality_str = "maj"  # Default to major if no quality specified

    # Normalize quality string
    q_lower = quality_str.lower()
    if q_lower == "" or q_lower == "major":
        quality_str = "maj"
    elif q_lower == "minor" or q_lower == "mi":
        quality_str = "min"
    elif q_lower == "dominant7" or q_lower == "dom7":
        quality_str = "7"
    # Add more specific aliases as needed, e.g. for m7b5 vs ø

    intervals = CHORD_FORMULAS.get(quality_str)

    if intervals is None:
        # Simplified extension handling
        if quality_str.endswith("7"):
            base_quality = quality_str[:-1] if quality_str[:-1] else "maj" # C7 -> C
            base_intervals = CHORD_FORMULAS.get(base_quality)
            if base_intervals:
                seventh_interval = INTERVALS["m7"] # Default to dominant 7th
                if "maj" in quality_str or "M" in quality_str:
                    seventh_interval = INTERVALS["M7"]
                intervals = base_intervals + [seventh_interval]
        
        if intervals is None:
            log.warning(
                f"Unknown chord quality '{quality_str}' in chord: {original_chord_string}. "
                "Returning root note."
            )
            return [get_note_name(root_value, prefer_sharp)]

    chord_note_values = [(root_value + interval) % 12 for interval in intervals]

    final_prefer_sharp = prefer_sharp
    if len(root_note_str) > 1 and root_note_str[1] == 'b':
        final_prefer_sharp = False

    chord_notes = [get_note_name(val, final_prefer_sharp) for val in chord_note_values]

    log.debug(f"Parsed {original_chord_string} to notes: {chord_notes}")
    return chord_notes


def generate_scale(root_note_str: str, scale_type: str = "major") -> List[str]:
    """
    Generates notes for a given scale.
    """
    log.info(f"Generating {root_note_str} {scale_type} scale")
    root_value = get_note_value(root_note_str)
    if root_value is None:
        log.warning(f"Invalid root note for scale generation: {root_note_str}")
        return []

    SCALE_PATTERNS: Dict[str, List[int]] = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],  # Natural minor
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11],  # Ascending
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10]  # Minor pentatonic + b5
    }

    pattern = SCALE_PATTERNS.get(scale_type.lower())
    if not pattern:
        log.warning(f"Unknown scale type: {scale_type}. Defaulting to major.")
        pattern = SCALE_PATTERNS["major"]

    scale_values = [(root_value + interval) % 12 for interval in pattern]

    prefer_flats_for_scale = (
        len(root_note_str) > 1 and root_note_str[1] == 'b'
    ) or root_note_str == "F"

    scale_notes = [
        get_note_name(val, prefer_sharp=not prefer_flats_for_scale)
        for val in scale_values
    ]
    log.debug(f"Generated {scale_type} scale for {root_note_str}: {scale_notes}")
    return scale_notes


def calculate_interval(note1_str: str, note2_str: str) -> Optional[str]:
    """
    Calculates the interval between two notes.
    """
    note_val1 = get_note_value(note1_str)
    note_val2 = get_note_value(note2_str)

    if note_val1 is None or note_val2 is None:
        log.warning(
            f"Could not calculate interval due to invalid note(s): {note1_str}, {note2_str}"
        )
        return None

    interval_value = (note_val2 - note_val1 + 12) % 12
    interval_name = VALUE_TO_INTERVAL_NAME.get(interval_value)

    log.info(
        f"Interval between {note1_str} and {note2_str} is {interval_name} "
        f"({interval_value} semitones)"
    )
    return interval_name
