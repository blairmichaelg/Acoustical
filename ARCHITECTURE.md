# Acoustic Cover Assistant - Project Architecture

This document outlines the high-level structure, data flow, and key components of the Acoustic Cover Assistant, reflecting its vision as a comprehensive tool for singer/songwriters.

---

## Overall Vision

To provide beginner/intermediate singer/songwriters with a seamless tool to analyze any song (via URL), extract chords, retrieve lyrics, synchronize them, and then offer creative ideas for flourishes, reharmonization, and practical fingering suggestions.

---

## Module Overview

*   **CLI (cli/):** Command-line interface built with Click. Provides modular commands for chord extraction (from local files or URLs), key analysis, transposition, capo advice, flourish generation, and lyrics retrieval.
*   **Web App (web_app/):** Flask backend with a minimal HTML/JS frontend. Allows users to upload audio files, paste URLs for audio/lyrics, extract chords, retrieve lyrics, analyze, and download results.
*   **chord_extraction/:** Handles chord extraction from audio using multiple backends (Chordino, autochord, chord-extractor). Supports plugin system and fallback logic. Now also orchestrates audio downloading from URLs via `audio_input.downloader`.
*   **key_transpose_capo/:** Implements key detection (music21), chord transposition, and capo recommendation logic.
*   **flourish_engine/:** Generates musical flourishes using rule-based, Magenta, and GPT4All backends. Extensible for new AI plugins.
*   **audio_input/:** Manages local audio files, handles YouTube/URL audio downloading (`yt-dlp` integration), and provides audio file validation utilities.
*   **common/:** Shared utilities for error formatting, serialization, and helpers.
*   **config.py:** Centralized configuration for backend preferences, output formats, and limits.
*   **tests/:** Organized tests for all modules and integration.

---

## Key Data Flows & Interactions

*   **Audio Processing Pipeline:**
    *   User provides audio (local file or URL).
    *   `chord_extraction.get_chords` processes input:
        *   If URL, `audio_input.downloader` downloads to a temporary file.
        *   Local file is validated.
    *   Chord extraction backends process audio.
    *   Results (chords with timestamps) are returned.
*   **Lyrics Retrieval:**
    *   User provides URL or song title/artist.
    *   Web App's `/get_lyrics` endpoint (or future dedicated module) fetches lyrics (e.g., from external APIs).
    *   Lyrics are returned.
*   **Analysis & Transformation:**
    *   Extracted chords are fed into `key_transpose_capo` for key detection, transposition, or capo advice.
    *   Chords (and potentially lyrics) are fed into `flourish_engine` for creative suggestions.
*   **Output:** Results are presented in CLI (JSON) or Web App (UI, downloadable JSON).

---

## Extensibility & Error Handling

*   **Plugin System:** New chord extraction or flourish backends can be registered via a simple API.
*   **Error Handling:** Fallback logic ensures robust extraction; errors are logged and reported to the user. Temporary files are managed for cleanup.
*   **Extensibility:** Modular design allows easy addition of new features, backends, and interfaces.

---

## Future Architectural Considerations (from [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md))

*   **Chord-Lyrics Synchronization:** Requires a new component for aligning time-stamped chords with lyrical text, potentially involving natural language processing (NLP) or advanced audio analysis.
*   **Advanced Flourish Generation:** Deeper integration of music theory will require more complex algorithms and potentially new data structures within `flourish_engine`.
*   **Intelligent Fingering Advisor:** A new dedicated module will be needed to model guitar fretboards, generate fingerings, and apply optimization heuristics.
*   **External API Integrations:** Expanding lyrics retrieval or other data sources will involve managing API keys, rate limits, and data parsing.

---

## High-Level Diagram

```mermaid
graph TD
    A[User Input: Local File / URL] --> B{Web App / CLI}
    B --> C[audio_input.downloader (for URLs)]
    C --> D[Temporary Audio File]
    A --> D
    D --> E[chord_extraction.get_chords]
    E --> F{Chord Extraction Backends}
    F --> G[Extracted Chords (with Timestamps)]

    B --> H[Lyrics Input: URL / Title+Artist]
    H --> I[Lyrics Retrieval (Placeholder API)]
    I --> J[Lyrics Text]

    G --> K{key_transpose_capo}
    G --> L{flourish_engine}
    G --> M{Future: Fingering Advisor}

    J --> N{Future: Chord-Lyrics Sync}
    G --> N

    K --> O[Key / Transposed Chords / Capo Advice]
    L --> P[Flourishes / Reharmonization]
    M --> Q[Fingering Suggestions]
    N --> R[Synchronized Chords & Lyrics]

    O --> S[Output: CLI / Web UI]
    P --> S
    Q --> S
    R --> S

    subgraph Core Modules
        E
        F
        G
        K
        L
        M
        N
    end

    subgraph Data Flow
        A
        B
        C
        D
        H
        I
        J
        O
        P
        Q
        R
        S
    end
```

For more details, see the README and each module's docstrings.
