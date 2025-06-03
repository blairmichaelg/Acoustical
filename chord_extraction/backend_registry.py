"""
Chord extraction backend registry and base interface.
"""

from typing import List, Dict, Any, Callable

class ChordExtractionBackend:
    """
    Base class for all chord extraction backends.
    Subclasses must implement is_available() and extract_chords(audio_path).
    """
    name = "base"

    @classmethod
    def is_available(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def extract_chords(cls, audio_path: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

# Registry for all backends
REGISTERED_BACKENDS: List[ChordExtractionBackend] = []
PLUGIN_BACKENDS: List[Callable[[str], List[Dict[str, Any]]]] = []

def register_backend(backend_cls):
    REGISTERED_BACKENDS.append(backend_cls)

def register_plugin_backend(plugin_func):
    PLUGIN_BACKENDS.append(plugin_func)

from config import BACKEND_ORDER

def get_available_backends():
    ordered_backends = sorted(REGISTERED_BACKENDS, key=lambda b: BACKEND_ORDER.index(b.name) if b.name in BACKEND_ORDER else len(BACKEND_ORDER))
    return [b for b in ordered_backends if b.is_available()]

def extract_chords_with_fallback(audio_path: str) -> List[Dict[str, Any]]:
    errors = []
    for backend in get_available_backends():
        try:
            return backend.extract_chords(audio_path)
        except Exception as e:
            errors.append(f"{backend.name}: {e}")
    for plugin in PLUGIN_BACKENDS:
        try:
            return plugin(audio_path)
        except Exception as e:
            errors.append(f"plugin {plugin}: {e}")
    raise RuntimeError(f"All chord extraction backends failed. Details: {errors}")
