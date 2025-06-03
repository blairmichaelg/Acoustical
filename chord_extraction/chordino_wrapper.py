"""
Chord extraction using Chordino (Vamp plugin) as a backend class.
"""

from typing import List, Dict, Union
import platform
import logging
from chord_extraction.backend_registry import ChordExtractionBackend, register_backend

class ChordinoBackend(ChordExtractionBackend):
    name = "chordino"

    @classmethod
    def is_available(cls) -> bool:
        try:
            import vamp  # type: ignore
            return platform.system() != 'Windows'
        except ImportError:
            return False

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        logger = logging.getLogger("chord_extraction.chordino_wrapper")
        if not cls.is_available():
            logger.warning("Chordino is not supported on this platform or vamp is missing. Use autochord or another backend.")
            raise NotImplementedError("Chordino is not supported on this platform or vamp is missing. Use autochord or another backend.")
        # If Chordino is available, implement actual extraction here.
        # For now, return dummy data for testability.
        logger.info(f"Extracting chords from {audio_path} using Chordino (stub).")
        return [{"time": 0.0, "chord": "C"}, {"time": 2.0, "chord": "G"}]

# Register backend on import
register_backend(ChordinoBackend)
