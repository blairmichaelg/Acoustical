"""
Chord extraction using chord-extractor backend as a backend class.
"""

from typing import List, Dict, Union
import subprocess
import json
import logging
import shutil
from chord_extraction.backend_registry import ChordExtractionBackend, register_backend

log = logging.getLogger(__name__) # Module-level logger

class ChordExtractorBackend(ChordExtractionBackend):
    name = "chord_extractor"

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which('chord-extractor') is not None

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        if not cls.is_available():
            log.error("chord-extractor CLI is not installed or not in PATH.")
            # Consider FileNotFoundError for more specificity
            raise RuntimeError("chord-extractor CLI is not installed or not in PATH.")
        try:
            log.info(f"Running chord-extractor CLI on {audio_path}")
            result = subprocess.run(
                ["chord-extractor", "--input", audio_path, "--output-format", "json"],
                capture_output=True, text=True, check=True, timeout=120
            )
            chords = json.loads(result.stdout)
            # Validate output format
            if not isinstance(chords, list) or not all(isinstance(c, dict) and "time" in c and "chord" in c for c in chords):
                log.error(f"Invalid output format from chord-extractor: {result.stdout[:200]}") # Log part of output
                raise ValueError("Invalid output format from chord-extractor")
            log.info(f"Extracted {len(chords)} chords from {audio_path} using chord-extractor.")
            return chords
        except subprocess.TimeoutExpired as e:
            log.error(f"chord-extractor timed out for {audio_path}: {e}")
            raise RuntimeError("chord-extractor backend timed out") from e
        except json.JSONDecodeError as e:
            # Ensure result is defined in this scope if json.loads fails early
            # It's defined after subprocess.run, so it should be fine.
            log.error(f"Failed to decode JSON output from chord-extractor for {audio_path}: {e}. Output: {result.stdout[:200] if 'result' in locals() and hasattr(result, 'stdout') else 'N/A'}")
            raise RuntimeError("chord-extractor returned invalid JSON") from e
        except subprocess.CalledProcessError as e:
            log.error(f"chord-extractor CLI returned non-zero exit code for {audio_path}: {e.returncode}. Stderr: {e.stderr}")
            raise RuntimeError("chord-extractor CLI failed") from e
        except ValueError as e: # Catch the specific ValueError from our validation
            log.error(f"Output validation failed for chord-extractor output from {audio_path}: {e}")
            raise # Re-raise the ValueError as is, so tests can catch it specifically
        except Exception as e: # General catch-all for other unexpected errors
            log.error(f"chord-extractor backend failed for {audio_path} with an unexpected error: {e}")
            raise RuntimeError("chord-extractor backend failed with an unexpected error") from e

# Register backend on import
register_backend(ChordExtractorBackend)
