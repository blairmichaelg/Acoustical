"""
Chord extraction using chord-extractor backend as a backend class.
"""

from typing import List, Dict, Union
import subprocess
import json
import logging
import shutil
from chord_extraction.backend_registry import ChordExtractionBackend, register_backend

class ChordExtractorBackend(ChordExtractionBackend):
    name = "chord_extractor"

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('chord-extractor') is not None

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        logger = logging.getLogger("chord_extraction.chord_extractor_util")
        if not cls.is_available():
            logger.error("chord-extractor CLI is not installed or not in PATH.")
            raise RuntimeError("chord-extractor CLI is not installed or not in PATH.")
        try:
            logger.info(f"Running chord-extractor CLI on {audio_path}")
            result = subprocess.run(
                ["chord-extractor", "--input", audio_path, "--output-format", "json"],
                capture_output=True, text=True, check=True, timeout=120
            )
            chords = json.loads(result.stdout)
            # Validate output format
            if not isinstance(chords, list) or not all("time" in c and "chord" in c for c in chords):
                logger.error("Invalid output format from chord-extractor")
                raise ValueError("Invalid output format from chord-extractor")
            logger.info(f"Extracted {len(chords)} chords from {audio_path} using chord-extractor.")
            return chords
        except subprocess.TimeoutExpired as e:
            logger.error(f"chord-extractor timed out: {e}")
            raise RuntimeError("chord-extractor backend timed out") from e
        except Exception as e:
            logger.error(f"chord-extractor backend failed: {e}")
            raise RuntimeError("chord-extractor backend failed") from e

# Register backend on import
register_backend(ChordExtractorBackend)
