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
import os
import mimetypes
import tempfile
from audio_input.downloader import download_audio # New import

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

def get_chords(audio_input_source: str) -> List[Dict[str, Any]]:
    """
    Extract chords from an audio file or URL using registered backends and plugins.
    If a URL is provided, the audio will be downloaded to a temporary file first.
    """
    log = logging.getLogger("chord_extraction")

    is_url = audio_input_source.startswith(("http://", "https://"))
    temp_file_path = None
    processed_audio_path = audio_input_source

    if is_url:
        try:
            log.info(f"Downloading audio from URL: {audio_input_source}")
            # Create a temporary directory for the downloaded file
            temp_dir = tempfile.mkdtemp()
            # download_audio returns the full path to the downloaded file
            downloaded_full_path = download_audio(audio_input_source, out_dir=temp_dir)
            processed_audio_path = downloaded_full_path
            temp_file_path = processed_audio_path # Store for cleanup
            log.info(f"Audio downloaded to: {processed_audio_path}")
        except Exception as e:
            log.error(f"Failed to download audio from URL {audio_input_source}: {e}")
            raise RuntimeError(f"Failed to download audio: {e}")
    else:
        # Pre-validate local audio file existence
        if not os.path.isfile(audio_input_source):
            log.error(f"Audio file not found: {audio_input_source}")
            raise FileNotFoundError(f"Audio file not found: {audio_input_source}")
        processed_audio_path = audio_input_source

    # Skip mime type check for .txt test files (or if it's a downloaded file that might not have a standard extension yet)
    if not processed_audio_path.endswith('.txt'):
        mime, _ = mimetypes.guess_type(processed_audio_path)
        if not (mime and mime.startswith("audio")):
            log.error(f"Unsupported or invalid audio file type: {processed_audio_path}")
            raise ValueError(f"Unsupported or invalid audio file type: {processed_audio_path}")

    from .backend_registry import extract_chords_with_fallback # Import here to avoid circular dependency if backend_registry imports get_chords
    try:
        chords = extract_chords_with_fallback(processed_audio_path)
        return chords
    finally:
        # Clean up temporary downloaded file and directory if applicable
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                # Also remove the temporary directory if it's empty
                if os.path.exists(os.path.dirname(temp_file_path)) and not os.listdir(os.path.dirname(temp_file_path)):
                    os.rmdir(os.path.dirname(temp_file_path))
            except OSError as e:
                log.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

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
