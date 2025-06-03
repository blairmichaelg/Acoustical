"""
Chord extraction using autochord as a backend class.
"""

from typing import List, Dict, Union
import logging
from chord_extraction.backend_registry import ChordExtractionBackend, register_backend

try:
    from autochord import guess_chords
except ImportError:
    guess_chords = None

class AutochordBackend(ChordExtractionBackend):
    name = "autochord"

    @classmethod
    def is_available(cls) -> bool:
        return guess_chords is not None

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        logger = logging.getLogger("chord_extraction.autochord_util")
        if not cls.is_available():
            logger.error("autochord is not installed. Please install with 'pip install autochord'.")
            raise ImportError("autochord is not installed. Please install with 'pip install autochord'.")
        try:
            logger.info(f"Extracting chords from {audio_path} using autochord.")
            chords = guess_chords(audio_path)
            # autochord returns a list of (time, chord) tuples
            return [{"time": float(t), "chord": str(c)} for t, c in chords]
        except Exception as e:
            logger.error(f"autochord extraction failed: {e}")
            raise RuntimeError("autochord extraction failed") from e

# Register backend on import
register_backend(AutochordBackend)
