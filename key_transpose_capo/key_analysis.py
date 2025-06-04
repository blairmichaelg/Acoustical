"""
Key analysis using music21's KrumhanslSchmuckler algorithm.
"""
from typing import List, Dict, Optional # Tuple removed, Counter removed
import logging
# from collections import Counter # No longer needed for heuristic
from music_theory import utils as mtu # Still needed for get_note_name if we parse root ourselves

log = logging.getLogger(__name__)

# Heuristic related constants and functions are removed for now.

def detect_key_from_chords(chord_list: List[str]) -> Dict[str, Optional[str]]:
    log.debug(f"Detecting key for: {chord_list} using music21 KrumhanslSchmuckler.")
    
    if not chord_list:
        log.warning("Empty chord list provided for key detection.")
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "Empty chord list."}

    try:
        from music21 import stream, harmony, analysis, pitch
        s = stream.Stream()
        valid_chords_added = 0
        for c_str in chord_list:
            if not c_str or not isinstance(c_str, str):
                log.debug(f"Skipping invalid chord input: {c_str}")
                continue
            try:
                chord_obj = harmony.ChordSymbol(c_str)
                log.debug(f"Parsed '{c_str}' to music21 ChordSymbol: Root: {chord_obj.root().name}, Quality: {chord_obj.quality}")
                s.append(chord_obj)
                valid_chords_added += 1
            except Exception as e_parse:
                log.debug(f"Could not parse chord '{c_str}' with music21: {e_parse}")
                continue
        
        if valid_chords_added == 0:
            log.warning("No valid chords found in list for music21 key detection.")
            return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "No valid chords for music21 key detection."}

        analyzer = analysis.discrete.KrumhanslSchmuckler()
        key_solution = analyzer.getSolution(s)
        log.debug(f"music21 key_solution: Tonic={key_solution.tonic}, Mode={key_solution.mode}, CC={key_solution.correlationCoefficient if hasattr(key_solution, 'correlationCoefficient') else 'N/A'}")
        
        key_root_name = None
        if isinstance(key_solution.tonic, pitch.Pitch):
            key_root_name = key_solution.tonic.name
        elif key_solution.tonic is not None: # Fallback if tonic is not a Pitch object but has a name
             key_root_name = str(key_solution.tonic)

        # Ensure root name is just the pitch class (e.g. "C", "C#", not "C4")
        if key_root_name and len(key_root_name) > 1 and key_root_name[-1].isdigit():
            key_root_name = key_root_name[:-1]

        key_quality = key_solution.mode if key_solution.mode else None # 'major' or 'minor'
        
        if key_root_name and key_quality:
            full_name = f"{key_root_name} {key_quality}"
            log.info(f"Detected key (music21): {full_name} from {valid_chords_added} valid chords.")
            return {"key_root": key_root_name, "key_quality": key_quality, "full_key_name": full_name}
        else:
            log.warning(f"KrumhanslSchmuckler analysis did not yield a clear key: Root='{key_root_name}', Mode='{key_quality}'")
            return {"key_root": key_root_name, "key_quality": key_quality, "full_key_name": None, "error": "Key analysis inconclusive (music21)."}

    except ImportError:
        log.error("music21 library not found. Key detection unavailable.")
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": "music21 library not found."}
    except Exception as e:
        log.error(f"Key detection failed with music21: {e}", exc_info=True)
        return {"key_root": None, "key_quality": None, "full_key_name": None, "error": f"Music21 key detection failed: {str(e)}"}
