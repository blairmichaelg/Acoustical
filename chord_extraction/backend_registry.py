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
    # Store the class itself, or its extract_chords method. Storing class allows access to .name
    # For now, let's assume we want to register the extract_chords method as before.
    # A more robust registry might store (name, class) or (name, method).
    if hasattr(cls, "extract_chords") and callable(cls.extract_chords):
        if cls.extract_chords not in _registered_plugins:  # Avoid duplicates
            _registered_plugins.append(cls.extract_chords)
    return cls


def unregister_backend_by_method(method_to_remove: Callable) -> None:
    """Unregister a backend by its extract_chords method."""
    try:
        _registered_plugins.remove(method_to_remove)
    except ValueError:
        # Method not found, already unregistered, or never registered
        pass


def get_registered_plugins() -> List[Callable]:
    """Return a copy of the list of registered plugin methods."""
    return list(_registered_plugins)


def extract_chords_with_fallback(audio_path: str) -> List[Dict[str, Any]]:
    """Try each backend in order until one succeeds."""
    # Try built-in backends first
    # Updated to use essentia_wrapper instead of chordino_wrapper
    from . import autochord_util, chord_extractor_util, essentia_wrapper

    for backend in [
        autochord_util.AutochordBackend.extract_chords,
        chord_extractor_util.ChordExtractorBackend.extract_chords,
        essentia_wrapper.EssentiaBackend.extract_chords,
        *_registered_plugins,  # Then try registered plugins
    ]:
        try:
            result = backend(audio_path)
            if result:
                return result
        except Exception:  # noqa: E722
            continue

    raise RuntimeError("All chord extraction backends failed or returned no results.")
