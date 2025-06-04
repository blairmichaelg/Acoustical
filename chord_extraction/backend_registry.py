"""
Backend registry for chord extraction plugins.

Manages registration and fallback logic for chord extraction backends.
"""

from typing import List, Dict, Any, Callable
from abc import ABC, abstractmethod


class ChordExtractionBackend(ABC):
    """Abstract base class for chord extraction backends."""
    
    @abstractmethod
    def extract_chords(self, audio_path: str) -> List[Dict[str, Any]]:
        """Extract chords from audio file."""
        pass


# Registry of plugin backends
_registered_plugins = []


def register_plugin_backend(
    backend_func: Callable[[str], List[Dict[str, Any]]]
) -> None:
    """Register a plugin backend function."""
    _registered_plugins.append(backend_func)


def register_backend(cls):
    """Class decorator to register a ChordExtractionBackend implementation."""
    _registered_plugins.append(cls.extract_chords)
    return cls


def extract_chords_with_fallback(audio_path: str) -> List[Dict[str, Any]]:
    """Try each backend in order until one succeeds."""
    # Try built-in backends first
    from . import chordino_wrapper, autochord_util, chord_extractor_util
    
    for backend in [
        chordino_wrapper.ChordinoBackend.extract_chords,
        autochord_util.AutochordBackend.extract_chords,
        chord_extractor_util.ChordExtractorBackend.extract_chords,
        *_registered_plugins  # Then try registered plugins
    ]:
        try:
            result = backend(audio_path)
            if result:
                return result
        except Exception:  # noqa: E722
            continue
    
    raise RuntimeError(
        "All chord extraction backends failed or returned no results."
    )
