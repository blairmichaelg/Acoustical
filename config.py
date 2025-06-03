"""
Centralized configuration for Acoustic Cover Assistant.
"""

# Default settings
DEFAULT_OUTPUT_FORMAT = "json"
MAX_AUDIO_FILE_SIZE_MB = 20
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac"}

# Backend preferences
BACKEND_ORDER = ["chordino", "autochord", "chord_extractor"]

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(levelname)s: %(message)s"

# Rule-based flourish substitution sets
RULE_BASED_SUBSTITUTIONS = {
    "default": {
        "C": "Am", "Am": "C",
        "D": "Bm", "Bm": "D",
        "G": "Em", "Em": "G",
        "F": "Dm", "Dm": "F"
    },
    "simplify": {
        "C7": "C", "Cm7": "Cm",
        "D7": "D", "Dm7": "Dm",
        "E7": "E", "Em7": "Em",
        "F7": "F", "Fm7": "Fm",
        "G7": "G", "Gm7": "Gm",
        "A7": "A", "Am7": "Am",
        "B7": "B", "Bm7": "Bm",
        "Cmaj7": "C", "Cmin7": "Cm",
        # Add more simplification rules as needed
    },
    "jazz": {
        "C": "Cmaj7", "Dm": "Dm7", "G": "G7",  # Simple II-V-I example
        "Am": "Am7", "Em": "Em7",
        # Add more jazz substitution rules as needed
    },
    "blues": {
        "C": "C7", "F": "F7", "G": "G7",  # Simple I-IV-V blues
        "A": "A7", "D": "D7", "E": "E7",
        # Add more blues substitution rules as needed
    }
}
