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

# Chord formulas: semitones from root
CHORD_FORMULAS: Dict[str, List[int]] = {
    # Triads
    "maj": [0, 4, 7],  # Major
    "m": [0, 3, 7],  # Minor
    "min": [0, 3, 7], # Alias for minor
    "dim": [0, 3, 6],  # Diminished
    "aug": [0, 4, 8],  # Augmented
    "sus4": [0, 5, 7], # Sus4
    "sus2": [0, 2, 7], # Sus2
    # Sevenths
    "7": [0, 4, 7, 10],  # Dominant 7th
    "maj7": [0, 4, 7, 11],  # Major 7th
    "M7": [0, 4, 7, 11], # Alias
    "m7": [0, 3, 7, 10],  # Minor 7th
    "min7": [0, 3, 7, 10], # Alias
    "m7b5": [0, 3, 6, 10],  # Half-diminished 7th
    "dim7": [0, 3, 6, 9],  # Diminished 7th (uses d7 interval which is 9 semitones)
    # Sixths
    "6": [0, 4, 7, 9], # Major 6th
    "m6": [0, 3, 7, 9], # Minor 6th
    # Ninths (basic versions, can be extended)
    "9": [0, 4, 7, 10, 2 + 12], # Dominant 9th (M2 in next octave)
    "maj9": [0, 4, 7, 11, 2 + 12], # Major 9th
    "m9": [0, 3, 7, 10, 2 + 12], # Minor 9th
    # Add chords
    "add9": [0, 4, 7, 2 + 12], # Major add9
    "madd9": [0, 3, 7, 2 + 12], # Minor add9
}

# Ordered list of (regex_pattern_for_quality, CHORD_FORMULAS_key)
# More specific patterns should come first.
# The regex matches the *end* of the quality string.
CHORD_QUALITY_PATTERNS = [
    (re.compile(r"m7b5$"), "m7b5"),
    (re.compile(r"maj9$"), "maj9"),
    (re.compile(r"m9$"), "m9"),
    (re.compile(r"add9$"), "add9"), # Check before "9"
    (re.compile(r"madd9$"), "madd9"),
    (re.compile(r"9$"), "9"), # Dominant 9
    (re.compile(r"maj7$"), "maj7"),
    (re.compile(r"M7$"), "M7"),
    (re.compile(r"m7$"), "m7"),
    (re.compile(r"min7$"), "min7"),
    (re.compile(r"dim7$"), "dim7"),
    (re.compile(r"7$"), "7"), # Dominant 7
    (re.compile(r"m6$"), "m6"),
    (re.compile(r"6$"), "6"),
    (re.compile(r"sus4$"), "sus4"),
    (re.compile(r"sus2$"), "sus2"),
    (re.compile(r"dim$"), "dim"),
    (re.compile(r"aug$"), "aug"),
    (re.compile(r"m$"), "m"),
    (re.compile(r"min$"), "min"),
    (re.compile(r"maj$"), "maj"), # Explicit "maj"
    (re.compile(r"$"), "maj"),    # Empty string implies major (matches end of string)
]


def get_note_value(note_str: str) -> Optional[int]:
    """Parses a note string (e.g., "C", "C#4", "Db3") and returns its numerical pitch class value (0-11)."""
    if not isinstance(note_str, str): # Handle potential non-string inputs gracefully
        log.warning(f"Invalid input type for note_str: {type(note_str)}. Expected string.")
        return None
        
    note_str_processed = note_str.strip().capitalize()
    
    # Handle common alternative names
    if note_str_processed == "H":
        note_str_processed = "B"
    
    # Strip octave numbers and other non-essential characters for pitch class lookup
    # Regex to extract the core note name (C, C#, Db etc.)
    match = re.match(r"([A-G][#b]?)", note_str_processed)
    if not match:
        log.warning(f"Could not extract valid note name from: {note_str}")
        return None
    
    core_note_name = match.group(1)
        
    val = NOTE_TO_VALUE.get(core_note_name)
    if val is None:
        log.warning(f"Could not parse note: {note_str}")
    return val


def get_note_name(note_value: int, prefer_sharp: bool = True) -> str:
    """Converts a numerical value back to a note name."""
    note_value = note_value % 12
    if prefer_sharp:
        return VALUE_TO_NOTE_SHARP.get(note_value, "N/A")
    else:
        return VALUE_TO_NOTE_FLAT.get(note_value, "N/A")


def parse_chord_to_notes(chord_string: str, prefer_sharp_for_output: bool = True) -> List[str]:
    """
    Parses a chord string into its constituent notes.
    """
    log.info(f"Parsing chord: {chord_string}")
    original_chord_string = chord_string

    # Normalize H to B before regex matching
    processed_chord_string = chord_string.replace("H", "B")

    # Regex to capture root note (C, C#, Db, etc.)
    root_match = re.match(r"([A-G][#b]?)", processed_chord_string)
    if not root_match:
        log.warning(f"Could not parse root note from chord: {original_chord_string}")
        return [original_chord_string] # Return original if unparseable

    root_note_str = root_match.group(1)
    root_value = get_note_value(root_note_str)
    if root_value is None: # Should be caught by get_note_value's logging
        # If root_match succeeded but get_note_value failed (e.g. "Hx"), it's an invalid root.
        # If root_match failed, original_chord_string is returned earlier.
        return [original_chord_string]

    quality_str = processed_chord_string[len(root_note_str):].strip()
    
    formula_key_to_use = None
    # Iterate through patterns to find the best match for the quality string
    for pattern, key in CHORD_QUALITY_PATTERNS:
        # We are matching the quality string itself, not just the end.
        # The regexes in CHORD_QUALITY_PATTERNS should be designed to match the full quality.
        # For example, r"m7b5$" should match "m7b5".
        # Let's adjust to match the whole quality string.
        # For now, let's assume the patterns are meant to match the *entire* quality string.
        # A simple direct lookup or a loop with exact matches might be better if regexes are complex.
        
        # Simplified: direct lookup for now, then refine with regex if needed for complex cases like C(add9)
        if quality_str == key: # Exact match for simple keys like "m", "maj7"
            formula_key_to_use = key
            break
        # For patterns that are regexes (like if we had r"m(aj)?7"):
        # if pattern.fullmatch(quality_str): # Use fullmatch if regex is for the whole quality string
        #     formula_key_to_use = key
        #     break
            
    if not formula_key_to_use: # If no exact match, try the regex patterns
        for pattern_regex, key_from_regex in CHORD_QUALITY_PATTERNS:
             # Ensure pattern_regex is a compiled regex object
            if isinstance(pattern_regex, re.Pattern) and pattern_regex.fullmatch(quality_str):
                formula_key_to_use = key_from_regex
                break
    
    # If still no key, and quality_str is empty, it's major.
    if not formula_key_to_use and not quality_str:
        formula_key_to_use = "maj"


    intervals = None
    if formula_key_to_use:
        intervals = CHORD_FORMULAS.get(formula_key_to_use)

    if intervals is None:
        log.warning(
            f"Unknown chord quality '{quality_str}' (resolved to key '{formula_key_to_use}') "
            f"in chord: {original_chord_string}. Returning root note."
        )
        return [get_note_name(root_value, prefer_sharp_for_output)]

    # Adjust intervals for notes like 9ths, 11ths, 13ths to be in the correct octave
    # The CHORD_FORMULAS already handle this by adding +12 where needed.
    chord_note_values = sorted(list(set([(root_value + interval) % 12 for interval in intervals])))


    # Determine sharp/flat preference for output notes
    final_prefer_sharp = prefer_sharp_for_output
    # If root is flat (Db, Eb, Gb, Ab, Bb), or F, prefer flats for display.
    if (len(root_note_str) > 1 and root_note_str[1] == 'b') or root_note_str == "F":
        final_prefer_sharp = False
    
    # For C major and G major, prefer sharps (natural notes, no accidentals needed for key itself)
    if root_note_str in ["C", "G"] and formula_key_to_use == "maj":
        final_prefer_sharp = True


    chord_notes = [get_note_name(val, final_prefer_sharp) for val in chord_note_values]
    
    log.debug(f"Parsed '{original_chord_string}' (root: {root_note_str}, quality: '{quality_str}', formula_key: '{formula_key_to_use}') to notes: {chord_notes}")
    return chord_notes


def generate_scale(root_note_str: str, scale_type: str = "major") -> List[str]:
    log.info(f"Generating {root_note_str} {scale_type} scale")
    root_value = get_note_value(root_note_str)
    if root_value is None:
        return []

    SCALE_PATTERNS: Dict[str, List[int]] = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11], 
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10]
    }

    pattern = SCALE_PATTERNS.get(scale_type.lower())
    if not pattern:
        log.warning(f"Unknown scale type: {scale_type}. Defaulting to major.")
        pattern = SCALE_PATTERNS["major"]

    scale_values = [(root_value + interval) % 12 for interval in pattern]
    
    prefer_flats_for_scale = (len(root_note_str) > 1 and root_note_str[1] == 'b') or root_note_str == "F"
    
    scale_notes = [get_note_name(val, prefer_sharp=not prefer_flats_for_scale) for val in scale_values]
    log.debug(f"Generated {scale_type} scale for {root_note_str}: {scale_notes}")
    return scale_notes


def calculate_interval(note1_str: str, note2_str: str) -> Optional[str]:
    note_val1 = get_note_value(note1_str)
    note_val2 = get_note_value(note2_str)

    if note_val1 is None or note_val2 is None:
        return None

    interval_value = (note_val2 - note_val1 + 12) % 12
    interval_name = VALUE_TO_INTERVAL_NAME.get(interval_value)
    
    log.info(
        f"Interval between {note1_str} and {note2_str} is {interval_name} "
        f"({interval_value} semitones)"
    )
    return interval_name
