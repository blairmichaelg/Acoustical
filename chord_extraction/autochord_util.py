"""
Chord extraction using autochord as a backend class.
"""

import logging
from typing import Dict, List, Union

from chord_extraction.backend_registry import (
    ChordExtractionBackend,
    register_backend,
)

try:
    from autochord import guess_chords
except ImportError:
    guess_chords = None


log = logging.getLogger(__name__)


class AutochordBackend(ChordExtractionBackend):
    name = "autochord"

    @classmethod
    def is_available(cls) -> bool:
        return guess_chords is not None

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        if not cls.is_available():
            log.warning("autochord is not installed. Skipping autochord backend.")
            return []
        try:
            log.info(f"Extracting chords from {audio_path} using autochord.")
            chords = guess_chords(audio_path)
            return [{"time": float(t), "chord": str(c)} for t, c in chords]
        except Exception as e:
            log.error(
                f"autochord extraction failed for {audio_path}: {e}", exc_info=True
            )
            raise RuntimeError(f"autochord extraction failed: {e}") from e


register_backend(AutochordBackend)
