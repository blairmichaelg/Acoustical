"""
Chord extraction using Essentia as a backend class.
"""

import logging
from typing import Dict, List, Union

from chord_extraction.backend_registry import (
    ChordExtractionBackend,
    register_backend,
)

try:
    import essentia
    import essentia.standard as es

    ESSENTIA_AVAILABLE = True
    log = logging.getLogger(__name__)
    log.debug("Essentia and essentia.standard imported successfully at module level.")
except ImportError:
    essentia = None  # type: ignore
    es = None  # type: ignore
    ESSENTIA_AVAILABLE = False
    if "log" not in globals():
        log = logging.getLogger(__name__)
    log.debug(
        "Essentia library not found at module level import, "
        "EssentiaBackend will be unavailable."
    )


ESSENTIA_TO_COMMON_CHORD = {
    "maj": "",
    "min": "m",
    "aug": "aug",
    "dim": "dim",
    "dom7": "7",
    "maj7": "maj7",
    "min7": "m7",
}


class EssentiaBackend(ChordExtractionBackend):
    name = "essentia"

    @classmethod
    def is_available(cls) -> bool:
        return ESSENTIA_AVAILABLE

    @classmethod
    def _format_essentia_chord_label(cls, essentia_label: str) -> str:
        if essentia_label == "N":
            return "N.C."
        parts = essentia_label.split(":")
        root = parts[0]
        quality = parts[1] if len(parts) > 1 else "maj"
        suffix = ESSENTIA_TO_COMMON_CHORD.get(quality, quality)
        if quality in ["7", "maj7", "m7", "dim7", "aug", "dim", "sus4", "sus2"]:
            suffix = quality
        elif quality == "major":
            suffix = ""
        elif quality == "minor":
            suffix = "m"
        if suffix.startswith(root) and len(suffix) > len(root):
            return suffix
        return root + suffix

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Union[float, str]]]:
        if not cls.is_available():
            log.warning("Essentia library is not installed. Skipping Essentia backend.")
            return []

        if es is None:
            log.error(
                "Essentia standard module (es) is None; "
                "this should not happen if is_available passed."
            )
            raise RuntimeError(
                "Essentia standard module not available for extraction "
                "despite is_available passing."
            )

        try:
            log.info(f"Extracting chords from {audio_path} using Essentia.")

            loader = es.MonoLoader(filename=audio_path)
            audio_samples = loader()

            # Use a simpler beat tracker as RhythmExtractor2013 is causing issues
            rhythm_extractor = es.BeatTrackerDegara()
            beats = rhythm_extractor(audio_samples)
            log.debug(f"Essentia: Number of beats: {len(beats)}")
            log.debug(f"Type of audio_samples: {type(audio_samples)}")
            log.debug(f"Size of audio_samples: {audio_samples.size}")
            log.debug(f"Type of beats: {type(beats)}")
            log.debug(f"Size of beats: {beats.size}")

            if not beats.size:
                log.warning(
                    f"Essentia: No beats detected in {audio_path}. "
                    "Cannot perform beat-aligned chord detection."
                )
                return []

            chord_detector = es.ChordsDetectionBeats()

            # Explicitly ensure inputs are VectorReal
            audio_samples_vr = essentia.VectorReal(audio_samples)
            beats_vr = essentia.VectorReal(beats)
            essentia_chords, chord_strength = chord_detector(
                audio_samples_vr, beats_vr
            )

            output_chords: List[Dict[str, Union[float, str]]] = []
            for i, beat_time in enumerate(beats):
                if i < len(essentia_chords):
                    chord_label = essentia_chords[i]
                    formatted_chord = cls._format_essentia_chord_label(chord_label)
                    output_chords.append(
                        {"time": float(beat_time), "chord": formatted_chord}
                    )

            log.info(
                f"Extracted {len(output_chords)} chords from {audio_path} using Essentia."
            )
            return output_chords

        except Exception as e:
            log.error(
                f"Essentia chord extraction failed for {audio_path}: {e}",
                exc_info=True,
            )
            raise RuntimeError(f"Essentia chord extraction failed: {e}") from e


register_backend(EssentiaBackend)
