# Acoustic Cover Assistant - Project Architecture

This diagram shows the high-level structure and data flow of the project:

---

## Module Overview

- **CLI (cli/):** Command-line interface built with Click. Provides modular commands for chord extraction, key analysis, transposition, capo advice, and flourish generation.
- **Web App (web_app/):** Flask backend with minimal HTML/JS frontend. Allows users to upload audio, extract chords, analyze, and download results.
- **chord_extraction/:** Handles chord extraction from audio using multiple backends (Chordino, autochord, chord-extractor). Supports plugin system and fallback logic.
- **key_transpose_capo/:** Implements key detection (music21), chord transposition, and capo recommendation logic.
- **flourish_engine/:** Generates musical flourishes using rule-based, Magenta, and GPT4All backends. Extensible for new AI plugins.
- **audio_input/:** Audio file management and YouTube downloader integration.
- **common/:** Shared utilities for error formatting, serialization, and helpers.
- **config.py:** Centralized configuration for backend preferences, output formats, and limits.
- **tests/:** Organized tests for all modules and integration.

---

## Extensibility & Error Handling

- **Plugin System:** New chord extraction or flourish backends can be registered via a simple API.
- **Error Handling:** Fallback logic ensures robust extraction; errors are logged and reported to the user.
- **Extensibility:** Modular design allows easy addition of new features, backends, and interfaces.

> **TODO:** Expand with more details on data formats, sequence diagrams, and integration points as the project evolves.


```
+-------------------+         +---------------------+         +-------------------+
|   CLI (Click)     | <-----> |  Core Modules       | <-----> |  Web App (Flask)  |
+-------------------+         +---------------------+         +-------------------+
        |                              |                               |
        v                              v                               v
+-------------------+   +--------------------------+   +--------------------------+
| chord_extraction/ |   | key_transpose_capo/      |   | flourish_engine/         |
+-------------------+   +--------------------------+   +--------------------------+
        |                              |                               |
        v                              v                               v
+-------------------+   +--------------------------+   +--------------------------+
| Audio Input Files |   | Chord/Key/Capo Logic     |   | Flourish/AI Plugins      |
+-------------------+   +--------------------------+   +--------------------------+
        |                              |                               |
        +------------------------------+-------------------------------+
                                       |
                                       v
                              +-------------------+
                              |   Output/Results  |
                              +-------------------+
```

- **CLI** and **Web App** are entry points for users.
- **Core Modules** handle all music theory, extraction, and AI logic.
- **Data** flows from audio input through extraction, analysis, and optional AI flourish, then to output (JSON, UI, etc).

For more details, see the README and each module's docstrings.
