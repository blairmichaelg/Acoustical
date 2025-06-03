"""
Key analysis using music21's KrumhanslSchmuckler algorithm.
"""
from typing import List

def detect_key_from_chords(chord_list: List[str]) -> str:
    """
    Detect global key from a list of chords using music21.

    Args:
        chord_list (List[str]): List of chord names as strings.

    Returns:
        str: Detected key in the format "Tonic Mode" (e.g., "C major").

    Raises:
        RuntimeError: If no valid chords are found or key detection fails.
    """
    try:
        from music21 import stream, harmony, analysis
        s = stream.Stream()
        for c in chord_list:
            try:
                s.append(harmony.ChordSymbol(c))
            except Exception:
                continue
        if len(s) == 0:
            raise RuntimeError("No valid chords for key detection.")
        analyzer = analysis.discrete.KrumhanslSchmuckler()
        key = analyzer.getSolution(s)
        return key.tonic.name + " " + key.mode
    except Exception as e:
        raise RuntimeError(f"Key detection failed: {e}")
