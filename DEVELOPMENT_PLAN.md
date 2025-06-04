# Acoustical Project: Refined Medium-Term Development Plan

## Overall Vision
To provide beginner/intermediate singer/songwriters with a seamless tool to analyze any song (via URL), extract chords, retrieve lyrics, synchronize them, and then offer creative ideas for flourishes, reharmonization, and practical fingering suggestions.

## Phase 1: Enhanced Audio Input & Basic Lyrics Retrieval
*   **Goal:** Make the app significantly easier to use by allowing direct URL input for chord extraction, alongside general UI/UX improvements and the ability to fetch lyrics.
*   **Tasks:**
    *   **Implement Direct URL Input for Chord Extraction:**
        *   Modify `chord_extraction.get_chords` to accept URLs (internally handling `yt-dlp` download to a temporary file).
        *   Update CLI `extract-chords` command to accept URLs.
        *   Add a URL input field to `web_app/index.html` for chord extraction.
    *   **NEW: Basic Lyrics Retrieval:**
        *   Add functionality to fetch lyrics for a song given its title/artist (or from the YouTube URL metadata). This would likely involve integrating with a lyrics API (e.g., Genius, if a free/developer tier is available) or a web scraping module.
        *   Display retrieved lyrics in the web app, initially as plain text alongside the extracted chords.
    *   Detailed review of `web_app/index.html` for UI/UX and accessibility (e.g., clearer feedback, progress indicators, responsive design).
    *   Address any remaining minor code quality issues.

## Phase 2: Chord-Lyrics Synchronization & Song Structure
*   **Goal:** Integrate lyrics and chords more deeply, providing a comprehensive, synchronized view of the song.
*   **Tasks:**
    *   **Heuristic-based Chord-Lyrics Alignment:** Develop a basic algorithm to align extracted chords (with their timestamps) with lyrical lines or sections. This would be an initial, simpler approach, aiming for "placement-wise" synchronization rather than precise word-level alignment. It might involve:
        *   Identifying line breaks and sections in lyrics.
        *   Associating chords with the start of lyrical lines or phrases based on their timestamps.
    *   **Basic Song Structure Identification:** Implement logic to identify common song sections (e.g., verse, chorus, bridge) based on lyrical repetition patterns or changes in chord progressions.
    *   **Display Integration:** Present synced chords and lyrics in an intuitive, scrollable format in the web app.

## Phase 3: Advanced Flourish Generation & Chord Substitution
*   **Goal:** Empower singer/songwriters with more creative tools for song modification and reinterpretation.
*   **Tasks:**
    *   Research and integrate music theory concepts (e.g., voice leading, common melodic patterns, harmonic context) into `flourish_engine`.
    *   Enhance algorithms for sophisticated, contextually appropriate flourishes.
    *   **NEW: Basic Chord Substitution/Reharmonization:** Implement functionality to suggest alternative chords that fit the key, mood, or harmonic function of a progression.
    *   Update interfaces and create new tests for these features.

## Phase 4: Intelligent Fingering Advisor
*   **Goal:** Provide practical guitar fingering suggestions for chords and progressions, optimizing for ease and flow.
*   **Tasks:**
    *   Design data models to represent guitar fretboards, string tunings, and chord voicings.
    *   Develop algorithms for fingering generation and optimization (playability, progression flow).
    *   Create a new module for this functionality.
    *   Integrate into CLI and Web App (e.g., visual fretboard diagrams).

## Cross-Cutting Concerns (Throughout all Phases)
*   **Performance Monitoring:** Continuously monitor and optimize processing times, especially with new audio and text analysis components.
*   **Error Handling & User Feedback:** Ensure all user-facing messages are clear, actionable, and guide the user effectively.
*   **Modularity & Testability:** Maintain high standards for code organization and comprehensive testing.
