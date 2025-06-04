import logging
from typing import List, Tuple, Optional, Dict, NamedTuple

log = logging.getLogger(__name__)


class ChordShape(NamedTuple):
    """
    Represents a specific fingering for a chord.
    """
    name: str                                 # e.g., "C Major Open", "G Barre Fret 3"
    root_note_str: str                        # e.g., "C", "G"
    chord_type: str                           # e.g., "maj", "m7", "dom7"
    # (string_index, fret, finger_used (0=open, 1-4=finger, -1=muted))
    fingerings: List[Tuple[int, int, int]]
    base_fret: int = 0                        # For barre chords
    barre_strings: Optional[List[int]] = None # Strings covered by barre

    def __repr__(self):
        return (
            f"ChordShape(name='{self.name}', root='{self.root_note_str}', "
            f"type='{self.chord_type}', base_fret={self.base_fret}, "
            f"fingerings={self.fingerings})"
        )


# Initial library of common chord shapes
COMMON_CHORD_SHAPES: Dict[str, List[ChordShape]] = {
    "maj": [
        ChordShape(
            "E Shape Barre", "E", "maj",
            fingerings=[(0, 0, -1), (1, 2, 2), (2, 2, 3), (3, 1, 1), (4, 0, -1), (5, 0, -1)],
            base_fret=0  # Placeholder for movable
        ),
        ChordShape(
            "A Shape Barre", "A", "maj",
            fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 1), (3, 2, 2), (4, 2, 3), (5, 0, -1)],
            base_fret=0  # Placeholder for movable
        ),
        ChordShape(
            "C Major Open", "C", "maj",
            fingerings=[(0, -1, -1), (1, 3, 3), (2, 2, 2), (3, 0, 0), (4, 1, 1), (5, 0, 0)]
        ),
        ChordShape(
            "G Major Open", "G", "maj",
            fingerings=[(0, 3, 2), (1, 2, 1), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 3, 3)]
        ),
        ChordShape(
            "D Major Open", "D", "maj",
            fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 1), (4, 3, 2), (5, 2, 0)]
        ),
        ChordShape(
            "A Major Open", "A", "maj",
            fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 1), (3, 2, 2), (4, 2, 3), (5, 0, 0)]
        ),
        ChordShape(
            "E Major Open", "E", "maj",
            fingerings=[(0, 0, 0), (1, 2, 2), (2, 2, 3), (3, 1, 1), (4, 0, 0), (5, 0, 0)]
        ),
    ],
    "min": [
        ChordShape(
            "Em Shape Barre", "E", "min",
            fingerings=[(0, 0, -1), (1, 2, 2), (2, 2, 3), (3, 0, -1), (4, 0, -1), (5, 0, -1)],
            base_fret=0
        ),
        ChordShape(
            "Am Shape Barre", "A", "min",
            fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 2), (3, 2, 3), (4, 1, 1), (5, 0, -1)],
            base_fret=0
        ),
        ChordShape(
            "Am Minor Open", "A", "min",
            fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 2), (3, 2, 3), (4, 1, 1), (5, 0, 0)]
        ),
        ChordShape(
            "Em Minor Open", "E", "min",
            fingerings=[(0, 0, 0), (1, 2, 2), (2, 2, 3), (3, 0, 0), (4, 0, 0), (5, 0, 0)]
        ),
        ChordShape(
            "Dm Minor Open", "D", "min",
            fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 2), (4, 3, 3), (5, 1, 1)]
        ),
    ],
    "7": [  # Dominant 7ths
        ChordShape(
            "E7 Shape Barre", "E", "7",
            fingerings=[(0, 0, -1), (1, 2, 1), (2, 0, -1), (3, 1, 2), (4, 0, -1), (5, 0, -1)],
            base_fret=0
        ),
        ChordShape(
            "A7 Shape Barre", "A", "7",
            fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 1), (3, 0, -1), (4, 2, 2), (5, 0, -1)],
            base_fret=0
        ),
        ChordShape(
            "C7 Open", "C", "7",
            fingerings=[(0, -1, -1), (1, 3, 3), (2, 2, 2), (3, 3, 4), (4, 1, 1), (5, 0, 0)]
        ),
        ChordShape(
            "G7 Open", "G", "7",
            fingerings=[(0, 3, 3), (1, 2, 2), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 1, 1)]
        ),
        ChordShape(
            "D7 Open", "D", "7",
            fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 1), (4, 1, 2), (5, 2, 3)]
        ),
        ChordShape(
            "A7 Open", "A", "7",
            fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 1), (3, 0, 0), (4, 2, 2), (5, 0, 0)]
        ),
        ChordShape(
            "E7 Open", "E", "7",
            fingerings=[(0, 0, 0), (1, 2, 1), (2, 0, 0), (3, 1, 2), (4, 0, 0), (5, 0, 0)]
        ),
    ],
}


def get_shapes_for_chord(root_note_str: str, chord_type: str) -> List[ChordShape]:
    """
    Retrieves known chord shapes for a given root note and chord type.
    This will later handle transposing movable shapes.

    Args:
        root_note_str (str): The root note of the chord (e.g., "C", "G#").
        chord_type (str): The type of the chord (e.g., "maj", "min", "7").

    Returns:
        List[ChordShape]: A list of matching ChordShape objects.
    """
    normalized_type = chord_type.lower()
    if normalized_type in ["minor", "mi"]:
        normalized_type = "min"
    elif normalized_type in ["major", ""]:  # Empty string often implies major
        normalized_type = "maj"
    elif normalized_type in ["dominant7", "dom7"]:
        normalized_type = "7"

    shapes = []
    type_specific_shapes = COMMON_CHORD_SHAPES.get(normalized_type, [])

    for shape_template in type_specific_shapes:
        # For now, only return shapes if the root matches the template's root
        # Later, implement transposition for barre chords
        if shape_template.root_note_str == root_note_str:
            shapes.append(shape_template)
        # TODO: Implement transposition for movable shapes

    if not shapes:
        log.debug(
            f"No direct shapes found for {root_note_str}{normalized_type}. "
            "Transposition needed for barre shapes."
        )

    return shapes


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    c_major_shapes = get_shapes_for_chord("C", "maj")
    print(f"\nC Major Shapes: {len(c_major_shapes)}")
    for shape in c_major_shapes:
        print(shape)

    a_minor_shapes = get_shapes_for_chord("A", "min")
    print(f"\nA Minor Shapes: {len(a_minor_shapes)}")
    for shape in a_minor_shapes:
        print(shape)

    e_dom7_shapes = get_shapes_for_chord("E", "7")
    print(f"\nE Dominant 7 Shapes: {len(e_dom7_shapes)}")
    for shape in e_dom7_shapes:
        print(shape)

    f_sharp_major_shapes = get_shapes_for_chord("F#", "maj")
    print(f"\nF# Major Shapes (expect empty for now): {len(f_sharp_major_shapes)}")
    for shape in f_sharp_major_shapes:
        print(shape)
