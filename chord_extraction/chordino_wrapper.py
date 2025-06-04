"""
Chord extraction using Chordino (Vamp plugin) as a backend class.
"""

from typing import List, Dict, Union
import platform
import logging
from chord_extraction.backend_registry import ChordExtractionBackend, register_backend

log = logging.getLogger(__name__) # Module-level logger

class ChordinoBackend(ChordExtractionBackend):
    name = "chordino"

    @classmethod
    def is_available(cls) -> bool:
        try:
            import vamp  # type: ignore
            # To make it testable where vamp might be installed but platform is Windows
            if platform.system() == 'Windows':
                log.debug("Chordino backend via vamp is generally not supported/problematic on Windows.")
                return False
            return True
        except ImportError:
            log.debug("Python vamp package not found, Chordino backend unavailable.")
            return False

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        if not cls.is_available():
            # This log might be redundant if is_available already logs, but good for direct call context
            log.warning("Chordino is not supported on this platform or vamp is missing.")
            raise NotImplementedError("Chordino is not supported on this platform or vamp is missing.")
        
        # TODO: Implement actual Chordino extraction using the vamp library.
        # This will involve:
        # 1. Importing vamp.
        # 2. Loading audio data (e.g., with librosa, or if vamp handles paths).
        #    Need audio data, sample_rate.
        # 3. Identifying the correct Chordino plugin key (e.g., "nnls-chroma:chordino").
        # 4. Calling vamp.load_plugin() and plugin.process().
        # 5. Parsing the output features from Chordino (typically timestamps and chord labels).
        # 6. Transforming to the standard List[Dict] format.
        # 7. Adding robust error handling for vamp/plugin issues.

        log.info(f"Extracting chords from {audio_path} using Chordino (STUB - NOT IMPLEMENTED).")
        # Returning dummy data for now to allow basic registration and fallback testing.
        # In a real scenario, this would raise an error or return actual data.
        # For testing purposes of the registry, this stub might be okay,
        # but for actual use, it needs implementation.
        # raise NotImplementedError("Chordino extraction logic is not yet implemented.")
        return [{"time": 0.0, "chord": "C (stub)"}, {"time": 2.0, "chord": "G (stub)"}]


# Register backend on import
register_backend(ChordinoBackend)
