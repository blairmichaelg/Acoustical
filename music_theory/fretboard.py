import logging
from typing import List, Tuple, Optional, Any # Added Any
from . import utils as music_theory_utils

log = logging.getLogger(__name__)

DEFAULT_TUNING = ["E2", "A2", "D3", "G3", "B3", "E4"]  # Standard guitar tuning
# Note values for standard tuning: E=4, A=9, D=2, G=7, B=11, E=4 (relative to C=0)


class Fretboard:
    """
    Represents a guitar fretboard and provides methods to find note positions.
    """
    def __init__(self, tuning: Optional[List[str]] = None, num_frets: int = 22):
        """
        Initializes the Fretboard.

        Args:
            tuning (Optional[List[str]]): List of note names for open strings,
                                          from lowest to highest.
                                          Defaults to standard EADGBe tuning.
            num_frets (int): Number of frets on the fretboard. Defaults to 22.
        """
        self.tuning_str = tuning or DEFAULT_TUNING
        self.num_strings = len(self.tuning_str)
        self.num_frets = num_frets
        self.string_open_notes_values: List[Optional[int]] = []
        # string_idx, fret_idx -> note_value
        self.notes_on_fret: List[List[Optional[int]]] = []

        self._initialize_fretboard()

    def _initialize_fretboard(self):
        """Calculates and stores the note value for each fret on each string."""
        self.string_open_notes_values = [
            music_theory_utils.get_note_value(note_str) for note_str in self.tuning_str
        ]

        self.notes_on_fret = [
            [None for _ in range(self.num_frets + 1)] for _ in range(self.num_strings)
        ]

        for string_idx in range(self.num_strings):
            open_note_val = self.string_open_notes_values[string_idx]
            if open_note_val is None:
                log.warning(
                    f"Invalid open string note '{self.tuning_str[string_idx]}' "
                    f"for string {string_idx}. Skipping string."
                )
                continue

            for fret_idx in range(self.num_frets + 1):  # Include open string at fret 0
                note_val = (open_note_val + fret_idx) % 12
                self.notes_on_fret[string_idx][fret_idx] = note_val

        log.info(
            f"Fretboard initialized with tuning: {self.tuning_str}, {self.num_frets} frets."
        )

    def get_note_at(self, string_idx: int, fret_idx: int) -> Optional[int]:
        """
        Gets the numerical note value at a specific string and fret.

        Args:
            string_idx (int): The string index (0 for lowest E string in standard tuning).
            fret_idx (int): The fret index (0 for open string).

        Returns:
            Optional[int]: The numerical note value (0-11), or None if out of bounds.
        """
        if not (0 <= string_idx < self.num_strings and 0 <= fret_idx <= self.num_frets):
            log.warning(f"Position ({string_idx}, {fret_idx}) is out of fretboard bounds.")
            return None
        try:
            return self.notes_on_fret[string_idx][fret_idx]
        except IndexError:  # Should not happen with bounds check
            log.error(f"IndexError accessing notes_on_fret at ({string_idx}, {fret_idx}).")
            return None

    def get_note_name_at(
        self, string_idx: int, fret_idx: int, prefer_sharp: bool = True
    ) -> Optional[str]:
        """
        Gets the note name (e.g., "C#") at a specific string and fret.
        """
        note_val = self.get_note_at(string_idx, fret_idx)
        if note_val is not None:
            return music_theory_utils.get_note_name(note_val, prefer_sharp)
        return None

    def find_note_positions(
        self, note_name_or_value: Any, max_fret: Optional[int] = None
    ) -> List[Tuple[int, int]]:
        """
        Finds all positions (string, fret) on the fretboard for a given note.

        Args:
            note_name_or_value (Any): The note name (str, e.g., "C#") or
                                      numerical value (int, 0-11).
            max_fret (Optional[int]): The maximum fret to search up to.
                                      Defaults to all frets.

        Returns:
            List[Tuple[int, int]]: A list of (string_index, fret_index) tuples.
        """
        target_note_value: Optional[int]
        if isinstance(note_name_or_value, str):
            target_note_value = music_theory_utils.get_note_value(note_name_or_value)
        elif isinstance(note_name_or_value, int):
            target_note_value = note_name_or_value % 12
        else:
            log.warning(f"Invalid note_name_or_value type: {type(note_name_or_value)}")
            return []

        if target_note_value is None:
            log.warning(f"Could not determine target note value for: {note_name_or_value}")
            return []

        search_max_fret = max_fret if max_fret is not None else self.num_frets
        positions: List[Tuple[int, int]] = []

        for string_idx in range(self.num_strings):
            # Ensure string was initialized correctly
            if string_idx >= len(self.notes_on_fret) or \
               self.string_open_notes_values[string_idx] is None:
                continue
            for fret_idx in range(search_max_fret + 1):
                if self.notes_on_fret[string_idx][fret_idx] == target_note_value:
                    positions.append((string_idx, fret_idx))

        log.debug(
            f"Found {len(positions)} positions for note {note_name_or_value} "
            f"(value {target_note_value}) up to fret {search_max_fret}."
        )
        return positions


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fb = Fretboard()
    print(
        f"Note at string 0, fret 0: {fb.get_note_name_at(0,0)} "
        f"(Value: {fb.get_note_at(0,0)})"  # E
    )
    print(
        f"Note at string 1, fret 5: {fb.get_note_name_at(1,5)} "
        f"(Value: {fb.get_note_at(1,5)})"  # D
    )
    print(
        f"Note at string 5, fret 3: {fb.get_note_name_at(5,3)} "
        f"(Value: {fb.get_note_at(5,3)})"  # G
    )

    c_sharp_positions = fb.find_note_positions("C#")
    print(f"C# positions: {c_sharp_positions}")

    g_positions_fret_5 = fb.find_note_positions("G", max_fret=5)
    print(f"G positions up to fret 5: {g_positions_fret_5}")

    # Test with a different tuning
    drop_d_tuning = ["D2", "A2", "D3", "G3", "B3", "E4"]
    fb_drop_d = Fretboard(tuning=drop_d_tuning)
    print(
        f"\nDrop D Tuning - Note at string 0, fret 0: {fb_drop_d.get_note_name_at(0,0)}"  # D
    )
    print(
        f"Drop D Tuning - Note at string 0, fret 2: {fb_drop_d.get_note_name_at(0,2)}"  # E
    )
