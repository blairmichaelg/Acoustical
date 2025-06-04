"""
Key analysis using music21's KrumhanslSchmuckler algorithm.
"""
from typing import List, Dict, Optional
import logging

log = logging.getLogger(__name__)

def detect_key_from_chords(chord_list: List[str]) -> Dict[str, Optional[str]]:
    """
    Detect global key from a list of chords using music21.

    Args:
        chord_list (List[str]): List of chord names as strings.

    Returns:
        Dict[str, Optional[str]]: Detected key information, e.g.,
            {"key_root": "C", "key_quality": "major", "full_key_name": "C major"}
            or {"error": "message"} if detection fails.
    """
    if not chord_list:
        log.warning("Empty chord list provided for key detection.")
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "Empty chord list."}

    try:
        from music21 import stream, harmony, analysis, pitch # Added pitch
        s = stream.Stream()
        valid_chords_added = 0
        for c_str in chord_list:
            if not c_str or not isinstance(c_str, str): # Skip None or non-string
                log.debug(f"Skipping invalid chord input: {c_str}")
                continue
            try:
                # music21 ChordSymbol can be slow if it tries to parse complex extensions not needed for key analysis.
                # A simpler approach might be to extract just the root for key analysis if performance is an issue.
                # For now, using ChordSymbol for its robustness.
                chord_obj = harmony.ChordSymbol(c_str)
                s.append(chord_obj)
                valid_chords_added += 1
            except Exception as e_parse:
                log.debug(f"Could not parse chord '{c_str}' with music21: {e_parse}")
                continue
        
        if valid_chords_added == 0:
            log.warning("No valid chords found in list for key detection.")
            return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "No valid chords for key detection."}

        analyzer = analysis.discrete.KrumhanslSchmuckler()
        key_solution = analyzer.getSolution(s)
        
        key_root_name = None
        if isinstance(key_solution.tonic, pitch.Pitch):
            key_root_name = key_solution.tonic.name
        elif key_solution.tonic is not None: # Fallback if tonic is not a Pitch object but has a name
             key_root_name = str(key_solution.tonic)


        key_quality = key_solution.mode if key_solution.mode else None # 'major' or 'minor'
        
        if key_root_name and key_quality:
            full_name = f"{key_root_name} {key_quality}"
            log.info(f"Detected key: {full_name} from {valid_chords_added} valid chords.")
            return {"key_root": key_root_name, "key_quality": key_quality, "full_key_name": full_name}
        else:
            log.warning(f"KrumhanslSchmuckler analysis did not yield a clear key: Root='{key_root_name}', Mode='{key_quality}'")
            return {"key_root": key_root_name, "key_quality": key_quality, "full_key_name": None, "error": "Key analysis inconclusive."}

    except ImportError:
        log.error("music21 library not found. Key detection unavailable.")
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "music21 library not found."}
    except Exception as e:
        log.error(f"Key detection failed: {e}", exc_info=True)
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": f"Key detection failed: {str(e)}"}
