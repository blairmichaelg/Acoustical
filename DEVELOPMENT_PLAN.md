# Development Plan: Acoustic Cover Assistant

## Overview

This document details the architecture, milestones, and prioritized tasks for the project. Use it for onboarding, sprint planning, and tracking progress.

---

## Milestones & Timeline

| Week | Goals                                                                 |
|------|-----------------------------------------------------------------------|
| 1    | Set up environment; prototype chord extraction (Chordino, autochord)  |
| 2    | Build key detection; transpose & capo logic; unit tests               |
| 3    | Implement rule-based flourish engine; integrate Magenta improv_rnn    |
| 4    | Wire up GPT4All prompts; build CLI interface; initial end-to-end test |
| 5    | Develop minimal web interface; finalize docs; polish UI               |

---

## Module Breakdown

### 1. Chord Extraction

- Integrate Chordino (pyvamp), autochord, chord-extractor.
- Fallback logic: try each backend in order.
- Output: JSON list of `{time, chord}`.
- Optional: Add aubio/essentia for onset/section detection.

### 2. Key Analysis & Transposition

- Use music21 for key detection.
- Implement `transpose_chords(chords, interval)`.
- Unit tests with known charts.

### 3. Capo Advisor

- Score open vs. barre chords per fret.
- For each fret, transpose and score; pick minimum.
- Output: recommended fret, transposed chords.

### 4. Flourish & Suggestion Engine

- Rule-based substitutions (I↔vi, ii↔IV, V/V insertion).
- Magenta improv_rnn for embellishments.
- GPT4All for creative suggestions (offline LLM).

### 5. Interfaces & Integration

- CLI: Modular commands for each function.
- Web App: Flask backend, minimal HTML/JS frontend, project persistence.

### 6. Testing & Documentation

- Pytest for all modules, sample fixtures.
- Docstrings, sample I/O, onboarding README.

---

## Good Ideas & Optimizations

- Plugin system for new extraction/flourish backends.
- Batch processing for multiple files.
- Audio downloader integration.
- Chord chart/sequence visualization in web UI.
- Configurable pipelines (YAML/JSON).
- Graceful error handling and fallback.
- Cross-platform support.
- AI prompt template versioning.
- Continuous integration (GitHub Actions).
- Extensive examples in `/data` and `/tests`.

---

## Prioritized Task List

> **Note:** Keep this checklist up to date as tasks are completed. Link to relevant issues/PRs where possible.

1. [ ] Finalize and document chord extraction backends.
2. [ ] Implement fallback logic and error handling.
3. [ ] Build key detection and transposition functions.
4. [ ] Develop capo advisor algorithm and tests.
5. [ ] Scaffold rule-based flourish engine.
6. [ ] Integrate Magenta and GPT4All modules.
7. [ ] Build CLI commands for all core features.
8. [ ] Develop minimal Flask web interface.
9. [ ] Add batch processing and plugin support.
10. [ ] Expand tests and add sample data.
11. [ ] Set up CI and code quality checks.
12. [ ] Polish documentation and onboarding.

> **TODO:** Add links to issues/PRs for each item above.

---

## Known Limitations & Future Ideas

- Chordino and some dependencies are not supported on Windows.
- Large/corrupt audio files may cause extraction failures.
- Web UI is minimal; could be expanded with visualization and editing.
- Consider supporting more audio formats and languages.
- Explore cloud-based processing for large files.
- Add more AI/ML flourish models and plugin types.
- Improve onboarding and developer documentation.
- [Add more as project evolves.]

---

## Example JSON Output

```json
[
  {"time": 0.0, "chord": "G"},
  {"time": 2.5, "chord": "D"}
]
```

---

## AI Prompt Template

```
Given this chord progression in key of G: [G, Em, C, D]
And these lyrics: “I walked along the riverside…”
Suggest three chord substitutions or extensions that fit mood.
```

---

## Contact

Open issues or discussions on GitHub for support and ideas.
