"""
Capo advisor: recommends capo fret based on chord complexity heuristics.
"""
from typing import List, Tuple

def recommend_capo(chords: List[str]) -> Tuple[int, List[str]]:
    """
    Recommend a capo fret and return the transposed chord set.

    Scores each fret (0-7) by number of open chords, picks the best.

    Args:
        chords (List[str]): List of chord names as strings.

    Returns:
        Tuple[int, List[str]]: (recommended fret, list of transposed chords)

    Notes:
        Open chords are defined as {"C", "D", "E", "G", "A", "Em", "Am", "Dm"}.
        The function prefers the fret with the most open chords after transposition.
    """
    from music21 import chord as m21chord, pitch
    open_chords = {"C", "D", "E", "G", "A", "Em", "Am", "Dm"}
    best_fret = 0
    best_score = float('inf')
    best_transposed = chords
    for fret in range(0, 8):
        try:
            transposed = []
            for c in chords:
                ch = m21chord.Chord(c)
                ch = ch.transpose(fret)
                root = ch.root().name
                quality = ch.quality
                if quality == 'major':
                    name = root
                elif quality == 'minor':
                    name = root + 'm'
                else:
                    name = root + ch.commonName
                transposed.append(name)
            # Score: count non-open chords
            score = sum(1 for t in transposed if t not in open_chords)
            if score < best_score:
                best_score = score
                best_fret = fret
                best_transposed = transposed
        except Exception:
            continue
    return best_fret, best_transposed
