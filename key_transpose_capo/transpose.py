"""
Chord transposition utilities using music21.
"""
from typing import List

def transpose_chords(chords: List[str], interval: int) -> List[str]:
    """
    Transpose a list of chords by the given interval (in semitones) using music21.

    Args:
        chords (List[str]): List of chord names as strings.
        interval (int): Number of semitones to transpose.

    Returns:
        List[str]: List of transposed chord names.

    Raises:
        ValueError: If a chord cannot be parsed or transposed.
    """
    from music21 import harmony, pitch
    transposed = []
    for c in chords:
        try:
            # Use ChordSymbol for common chord names (e.g., Am, F#m, G7)
            cs = harmony.ChordSymbol(c)
            cs = cs.transpose(interval)
            # Output as string (e.g., 'Am', 'F#m', 'G7')
            transposed.append(cs.figure)
        except Exception:
            # Fallback: try as a single note
            try:
                p = pitch.Pitch(c)
                p = p.transpose(interval)
                transposed.append(p.name)
            except Exception:
                raise ValueError(f"Invalid chord: {c}")
    return transposed
