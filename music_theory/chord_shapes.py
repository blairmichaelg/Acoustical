import logging
from typing import List, Tuple, Optional, Dict, NamedTuple
from . import utils as music_theory_utils # For note value calculations

log = logging.getLogger(__name__)


class ChordShape(NamedTuple):
    """
    Represents a specific fingering for a chord.
    """
    name: str
    template_root_note_str: str  # Root of the *template* shape (e.g., "E")
    chord_type: str  # e.g., "maj", "m7"
    # (string_idx, fret_offset, finger (0=open relative to base, 1-4, -1=muted))
    fingerings: List[Tuple[int, int, int]]
    base_fret_of_template: int = 0  # Fret where template is rooted
    is_movable: bool = False
    barre_strings_offset: Optional[List[int]] = None # Strings barred in template

    def __repr__(self):
        return (
            f"ChordShape(name='{self.name}', "
            f"template_root='{self.template_root_note_str}', "
            f"type='{self.chord_type}', "
            f"base_fret_template={self.base_fret_of_template}, "
            f"movable={self.is_movable}, fingerings={self.fingerings})"
        )


COMMON_CHORD_SHAPE_TEMPLATES: Dict[str, List[ChordShape]] = {
    "maj": [
        ChordShape("E Shape Barre", "E", "maj", fingerings=[(0,0,1),(1,2,3),(2,2,4),(3,1,2),(4,0,1),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[0,4,5]),
        ChordShape("A Shape Barre", "A", "maj", fingerings=[(0,-1,-1),(1,0,1),(2,2,2),(3,2,3),(4,2,4),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[1,5]),
        ChordShape("C Major Open", "C", "maj", fingerings=[(0,-1,-1),(1,3,3),(2,2,2),(3,0,0),(4,1,1),(5,0,0)]),
        ChordShape("G Major Open", "G", "maj", fingerings=[(0,3,2),(1,2,1),(2,0,0),(3,0,0),(4,0,0),(5,3,3)]),
        ChordShape("D Major Open", "D", "maj", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,1),(4,3,2),(5,2,0)]),
        ChordShape("A Major Open", "A", "maj", fingerings=[(0,-1,-1),(1,0,0),(2,2,1),(3,2,2),(4,2,3),(5,0,0)]),
        ChordShape("E Major Open", "E", "maj", fingerings=[(0,0,0),(1,2,2),(2,2,3),(3,1,1),(4,0,0),(5,0,0)]),
    ],
    "min": [
        ChordShape("Em Shape Barre", "E", "min", fingerings=[(0,0,1),(1,2,3),(2,2,4),(3,0,1),(4,0,1),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[0,3,4,5]),
        ChordShape("Am Shape Barre", "A", "min", fingerings=[(0,-1,-1),(1,0,1),(2,2,3),(3,2,4),(4,1,2),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[1,5]),
        ChordShape("Am Minor Open", "A", "min", fingerings=[(0,-1,-1),(1,0,0),(2,2,2),(3,2,3),(4,1,1),(5,0,0)]),
        ChordShape("Em Minor Open", "E", "min", fingerings=[(0,0,0),(1,2,2),(2,2,3),(3,0,0),(4,0,0),(5,0,0)]),
        ChordShape("Dm Minor Open", "D", "min", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,2),(4,3,3),(5,1,1)]),
    ],
    "7": [
        ChordShape("E7 Shape Barre", "E", "7", fingerings=[(0,0,1),(1,2,3),(2,0,1),(3,1,2),(4,0,1),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[0,2,4,5]),
        ChordShape("A7 Shape Barre", "A", "7", fingerings=[(0,-1,-1),(1,0,1),(2,2,2),(3,0,1),(4,2,3),(5,0,1)], base_fret_of_template=0, is_movable=True, barre_strings_offset=[1,3,5]),
        ChordShape("C7 Open", "C", "7", fingerings=[(0,-1,-1),(1,3,3),(2,2,2),(3,3,4),(4,1,1),(5,0,0)]),
        ChordShape("G7 Open", "G", "7", fingerings=[(0,3,3),(1,2,2),(2,0,0),(3,0,0),(4,0,0),(5,1,1)]),
        ChordShape("D7 Open", "D", "7", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,1),(4,1,2),(5,2,3)]),
        ChordShape("A7 Open", "A", "7", fingerings=[(0,-1,-1),(1,0,0),(2,2,1),(3,0,0),(4,2,2),(5,0,0)]),
        ChordShape("E7 Open", "E", "7", fingerings=[(0,0,0),(1,2,1),(2,0,0),(3,1,2),(4,0,0),(5,0,0)]),
    ],
    "maj7": [
        ChordShape("Cmaj7 Open", "C", "maj7", fingerings=[(0,-1,-1),(1,3,3),(2,2,2),(3,0,0),(4,0,0),(5,0,0)]),
        ChordShape("Gmaj7 Open", "G", "maj7", fingerings=[(0,3,2),(1,2,1),(2,0,0),(3,0,0),(4,0,0),(5,2,0)]),
        ChordShape("Amaj7 Open", "A", "maj7", fingerings=[(0,-1,-1),(1,0,0),(2,2,2),(3,1,1),(4,2,0),(5,0,0)]),
        ChordShape("Dmaj7 Open", "D", "maj7", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,2),(4,2,3),(5,2,1)]),
    ],
    "m7": [
        ChordShape("Am7 Open", "A", "m7", fingerings=[(0,-1,-1),(1,0,0),(2,2,2),(3,0,0),(4,1,1),(5,0,0)]),
        ChordShape("Em7 Open", "E", "m7", fingerings=[(0,0,0),(1,2,0),(2,0,0),(3,0,0),(4,0,0),(5,0,0)]),
        ChordShape("Dm7 Open", "D", "m7", fingerings=[(0,-1,-1),(1,-1,-1),(2,0,0),(3,2,2),(4,1,1),(5,1,0)]),
    ],
}


def _transpose_shape(template: ChordShape, target_root_str: str) -> Optional[ChordShape]:
    """Transposes a movable template shape to a new root note."""
    if not template.is_movable:
        return None

    template_root_val = music_theory_utils.get_note_value(template.template_root_note_str)
    target_root_val = music_theory_utils.get_note_value(target_root_str)

    if template_root_val is None or target_root_val is None:
        log.warning("Invalid root note for transposition.")
        return None

    transposition_offset = (target_root_val - template_root_val + 12) % 12
    new_base_fret = template.base_fret_of_template + transposition_offset

    if new_base_fret < 0 or new_base_fret > 15:  # Practical fret limit
        log.debug(
            f"Transposed base_fret {new_base_fret} out of practical range for "
            f"{template.name} to {target_root_str}."
        )
        return None

    new_fingerings: List[Tuple[int, int, int]] = []
    for string_idx, fret_offset, finger in template.fingerings:
        if fret_offset == -1:  # Muted string
            new_fingerings.append((string_idx, -1, -1))
        else:
            actual_fret = new_base_fret + fret_offset
            new_fingerings.append((string_idx, actual_fret, finger))

    actual_barre_strings = template.barre_strings_offset

    return ChordShape(
        name=f"{template.name} for {target_root_str}",
        template_root_note_str=target_root_str, # New root
        chord_type=template.chord_type,
        fingerings=new_fingerings,
        base_fret_of_template=new_base_fret, # This is the new effective base/barre fret
        is_movable=True,
        barre_strings_offset=actual_barre_strings
    )


def get_shapes_for_chord(root_note_str: str, chord_type: str) -> List[ChordShape]:
    """
    Retrieves known chord shapes for a given root note and chord type,
    including transposed movable shapes.
    """
    normalized_type = chord_type.lower()
    if normalized_type in ["minor", "mi"]:
        normalized_type = "min"
    elif normalized_type in ["major", ""]:
        normalized_type = "maj"
    elif normalized_type in ["dominant7", "dom7"]:
        normalized_type = "7"
    # Ensure other types like "maj7", "m7" are passed through or normalized if needed

    shapes = []
    type_specific_templates = COMMON_CHORD_SHAPE_TEMPLATES.get(normalized_type, [])

    for template in type_specific_templates:
        if not template.is_movable:
            if template.template_root_note_str == root_note_str:
                shapes.append(template)
        else:  # Is movable
            transposed_shape = _transpose_shape(template, root_note_str)
            if transposed_shape:
                shapes.append(transposed_shape)

    if not shapes:
        log.debug(f"No shapes found for {root_note_str}{normalized_type}.")
    return shapes


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    tests = [
        ("C", "maj"), ("G", "maj"), ("F#", "maj"), ("Bb", "maj"),
        ("A", "min"), ("C#", "min"),
        ("E", "7"), ("B", "7"),
        ("G", "maj7"), ("D", "m7")
    ]
    for root, type_c in tests:
        shapes_found = get_shapes_for_chord(root, type_c)
        print(f"\n--- {root}{type_c} Shapes ({len(shapes_found)}) ---")
        for s in shapes_found:
            print(s)
