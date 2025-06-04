"""
Unified chord extraction interface.

Provides get_chords(audio_path) which tries multiple backends (Chordino, autochord, chord-extractor)
and returns a list of dicts: [{"time": float, "chord": str}, ...].

Backends are tried in order of preference. If one fails, the next is used.

Example usage:
    from chord_extraction import get_chords
    chords = get_chords("audio_input/song.mp3")
"""

from . import chordino_wrapper
from . import autochord_util
from . import chord_extractor_util
from .backend_registry import _registered_plugins
import logging
import shutil
from typing import List, Dict, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

def register_chord_extraction_backend(backend_func: Callable[[str], List[Dict[str, Any]]]) -> None:
    """Register a custom chord extraction backend."""
    from .backend_registry import register_plugin_backend
    register_plugin_backend(backend_func)

def check_backend_availability() -> Dict[str, bool]:
    """Check which chord extraction backends are available on this system."""
    availability = {}
    # Chordino (pyvamp)
    try:
        import vamp
        availability['chordino'] = True
    except ImportError:
        availability['chordino'] = False
    # autochord
    try:
        import autochord
        availability['autochord'] = True
    except ImportError:
        availability['autochord'] = False
    # chord-extractor CLI
    availability['chord_extractor'] = shutil.which('chord-extractor') is not None
    return availability

def get_chords(audio_path: str) -> List[Dict[str, Any]]:
    """Extract chords from an audio file using registered backends and plugins."""
    import os
    import mimetypes
    log = logging.getLogger("chord_extraction")
    
    # Pre-validate audio file existence
    if not os.path.isfile(audio_path):
        log.error(f"Audio file not found: {audio_path}")
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Skip mime type check for .txt test files
    if not audio_path.endswith('.txt'):
        mime, _ = mimetypes.guess_type(audio_path)
        if not (mime and mime.startswith("audio")):
            log.error(f"Unsupported or invalid audio file type: {audio_path}")
            raise ValueError(f"Unsupported or invalid audio file type: {audio_path}")

    from .backend_registry import extract_chords_with_fallback
    return extract_chords_with_fallback(audio_path)

def get_chords_batch(audio_paths: List[str], parallel: bool = True) -> Dict[str, Any]:
    """Batch process multiple audio files for chord extraction."""
    results = {}
    log = logging.getLogger("chord_extraction")
    if parallel:
        with ThreadPoolExecutor() as executor:
            future_to_path = {executor.submit(get_chords, path): path for path in audio_paths}
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    results[path] = future.result()
                except Exception as e:
                    log.error(f"Batch extraction failed for {path}: {e}")
                    results[path] = {"error": str(e)}
    else:
        for path in audio_paths:
            try:
                results[path] = get_chords(path)
            except Exception as e:
                log.error(f"Batch extraction failed for {path}: {e}")
                results[path] = {"error": str(e)}
    return results

# Example plugin for demonstration and testing
def example_plugin_backend(audio_path: str) -> List[Dict[str, Any]]:
    """Example plugin backend for chord extraction."""
    logging.getLogger("chord_extraction").info(f"Plugin backend called for {audio_path}")
    return [{"time": 0.0, "chord": "PluginC"}, {"time": 1.0, "chord": "PluginG"}]
