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
            base_fret=0  # Movable
        ),
        ChordShape(
            "A Shape Barre", "A", "maj",
            fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 1), (3, 2, 2), (4, 2, 3), (5, 0, -1)],
            base_fret=0  # Movable
        ),
        ChordShape("C Major Open", "C", "maj", fingerings=[(0, -1, -1), (1, 3, 3), (2, 2, 2), (3, 0, 0), (4, 1, 1), (5, 0, 0)]),
        ChordShape("G Major Open", "G", "maj", fingerings=[(0, 3, 2), (1, 2, 1), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 3, 3)]),
        ChordShape("D Major Open", "D", "maj", fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 1), (4, 3, 2), (5, 2, 0)]),
        ChordShape("A Major Open", "A", "maj", fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 1), (3, 2, 2), (4, 2, 3), (5, 0, 0)]),
        ChordShape("E Major Open", "E", "maj", fingerings=[(0, 0, 0), (1, 2, 2), (2, 2, 3), (3, 1, 1), (4, 0, 0), (5, 0, 0)]),
    ],
    "min": [
        ChordShape("Em Shape Barre", "E", "min", fingerings=[(0, 0, -1), (1, 2, 2), (2, 2, 3), (3, 0, -1), (4, 0, -1), (5, 0, -1)], base_fret=0), # Movable
        ChordShape("Am Shape Barre", "A", "min", fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 2), (3, 2, 3), (4, 1, 1), (5, 0, -1)], base_fret=0), # Movable
        ChordShape("Am Minor Open", "A", "min", fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 2), (3, 2, 3), (4, 1, 1), (5, 0, 0)]),
        ChordShape("Em Minor Open", "E", "min", fingerings=[(0, 0, 0), (1, 2, 2), (2, 2, 3), (3, 0, 0), (4, 0, 0), (5, 0, 0)]),
        ChordShape("Dm Minor Open", "D", "min", fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 2), (4, 3, 3), (5, 1, 1)]),
    ],
    "7": [  # Dominant 7ths
        ChordShape("E7 Shape Barre", "E", "7", fingerings=[(0, 0, -1), (1, 2, 1), (2, 0, -1), (3, 1, 2), (4, 0, -1), (5, 0, -1)], base_fret=0), # Movable
        ChordShape("A7 Shape Barre", "A", "7", fingerings=[(0, -1, -1), (1, 0, -1), (2, 2, 1), (3, 0, -1), (4, 2, 2), (5, 0, -1)], base_fret=0), # Movable
        ChordShape("C7 Open", "C", "7", fingerings=[(0, -1, -1), (1, 3, 3), (2, 2, 2), (3, 3, 4), (4, 1, 1), (5, 0, 0)]),
        ChordShape("G7 Open", "G", "7", fingerings=[(0, 3, 3), (1, 2, 2), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 1, 1)]),
        ChordShape("D7 Open", "D", "7", fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 1), (4, 1, 2), (5, 2, 3)]),
        ChordShape("A7 Open", "A", "7", fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 1), (3, 0, 0), (4, 2, 2), (5, 0, 0)]),
        ChordShape("E7 Open", "E", "7", fingerings=[(0, 0, 0), (1, 2, 1), (2, 0, 0), (3, 1, 2), (4, 0, 0), (5, 0, 0)]),
    ],
    "maj7": [
        ChordShape("Cmaj7 Open", "C", "maj7", fingerings=[(0, -1, -1), (1, 3, 3), (2, 2, 2), (3, 0, 0), (4, 0, 0), (5, 0, 0)]), # Variation of C
        ChordShape("Gmaj7 Open", "G", "maj7", fingerings=[(0, 3, 2), (1, 2, 1), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 2, 0)]), # Variation of G
        ChordShape("Amaj7 Open", "A", "maj7", fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 2), (3, 1, 1), (4, 2, 0), (5, 0, 0)]),
        ChordShape("Dmaj7 Open", "D", "maj7", fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 2), (4, 2, 3), (5, 2, 1)]),
        ChordShape("Emaj7 Barre (A-shape)", "E", "maj7", fingerings=[(0,-1,-1), (1,7,1), (2,9,3), (3,8,2), (4,9,4), (5,-1,-1)], base_fret=7, barre_strings=[1]), # Emaj7 at 7th fret A-shape
    ],
    "m7": [
        ChordShape("Am7 Open", "A", "m7", fingerings=[(0, -1, -1), (1, 0, 0), (2, 2, 2), (3, 0, 0), (4, 1, 1), (5, 0, 0)]),
        ChordShape("Em7 Open", "E", "m7", fingerings=[(0, 0, 0), (1, 2, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 0, 0)]), # Often played with 2nd finger on A string
        ChordShape("Dm7 Open", "D", "m7", fingerings=[(0, -1, -1), (1, -1, -1), (2, 0, 0), (3, 2, 2), (4, 1, 1), (5, 1, 0)]),
    ],
    "dim": [ # Diminished chords are often movable
        ChordShape("Cdim Movable", "C", "dim", fingerings=[(0,-1,-1), (1,3,2), (2,1,1), (3,3,3), (4,2,0), (5,-1,-1)], base_fret=0), # Example Cdim, can be moved
    ],
    "sus4": [
        ChordShape("Dsus4 Open", "D", "sus4", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,1),(4,3,3),(5,3,2)]),
        ChordShape("Asus4 Open", "A", "sus4", fingerings=[(0,-1,-1),(1,0,0),(2,2,1),(3,2,2),(4,3,3),(5,0,0)]),
        ChordShape("Esus4 Open", "E", "sus4", fingerings=[(0,0,0),(1,2,2),(2,2,3),(3,2,4),(4,0,0),(5,0,0)]),
    ]
}


def get_shapes_for_chord(root_note_str: str, chord_type: str) -> List[ChordShape]:
    """
    Retrieves known chord shapes for a given root note and chord type.
    This will later handle transposing movable shapes.
    """
    normalized_type = chord_type.lower()
    if normalized_type in ["minor", "mi"]:
        normalized_type = "min"
    elif normalized_type in ["major", ""]:
        normalized_type = "maj"
    elif normalized_type in ["dominant7", "dom7"]:
        normalized_type = "7"
    # Add more normalizations if CHORD_FORMULAS keys are different
    # e.g. maj7, min7, sus4 etc. should already match if keys are consistent

    shapes = []
    type_specific_shapes = COMMON_CHORD_SHAPES.get(normalized_type, [])

    for shape_template in type_specific_shapes:
        if shape_template.root_note_str == root_note_str:
            shapes.append(shape_template)
        # TODO: Implement transposition for movable shapes

    if not shapes:
        log.debug(
            f"No direct shapes found for {root_note_str}{normalized_type}. "
            "Transposition needed for barre shapes or shape not in library."
        )
    return shapes


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    tests = [("C", "maj"), ("A", "min"), ("E", "7"), ("G", "maj7"), ("D", "m7"), ("C", "dim"), ("A", "sus4")]
    for root, type_c in tests:
        shapes_found = get_shapes_for_chord(root, type_c)
        print(f"\n{root}{type_c} Shapes: {len(shapes_found)}")
        for s in shapes_found:
            print(s)

    f_sharp_major_shapes = get_shapes_for_chord("F#", "maj")
    print(f"\nF# Major Shapes (expect empty for now): {len(f_sharp_major_shapes)}")
