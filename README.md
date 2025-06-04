# Acoustic Cover Assistant

![CI](https://github.com/blairmichaelg/Acoustical/actions/workflows/python-app.yml/badge.svg)

A powerful, open-source tool designed for **beginner to intermediate singer/songwriters** to effortlessly analyze, adapt, and creatively transform songs. Acoustical provides a seamless pipeline to extract chords, retrieve lyrics, analyze key, transpose, recommend capo positions, and generate musical flourishes from any song, whether from a local file or a direct URL.

Our vision is to empower you to **think of any song and instantly get the chords, lyrics, and creative progression ideas**, helping you put your own unique spin on covers or build new compositions.

> **Note:** GitHub repository info has been updated.

---

## Audio Downloader

You can download audio from YouTube and other sites using the built-in downloader (requires `yt-dlp`):

**Install yt-dlp:**
```
pip install yt-dlp
```

**Python usage:**
```python
from audio_input.downloader import download_audio
download_audio("https://www.youtube.com/watch?v=...", out_dir="audio_input")
```

**Command-line usage:**
```
python audio_input/downloader.py <url> [--out_dir audio_input]
```

## Quickstart

1.  **Clone the repo and create a Python 3.11+ virtual environment.**
2.  **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```
    For advanced features (audio analysis, flourishes), uncomment optional lines in requirements.txt or use Poetry/Pipenv.
3.  **Run tests:**
    ```
    make test
    ```
4.  **Start the web app:**
    ```
    python web_app/app.py
    ```
    Open your browser at [http://localhost:5000](http://localhost:5000)

---

## Features

*   **Intelligent Chord Extraction:** Get chords from any audio file or direct URL (YouTube, etc.).
*   **Basic Lyrics Retrieval:** Fetch lyrics for songs using their URL or by providing title and artist.
*   **Key Detection & Transposition:** Analyze song key and easily transpose chords to fit your vocal range or preferred key.
*   **Capo Recommendation:** Get smart capo suggestions to simplify complex chord progressions.
*   **Creative Flourish Generation:** Generate musical embellishments (rule-based, Magenta, GPT4All) to add your unique touch.
*   **CLI & Web App Interfaces:** Interact with the tool via command line or a user-friendly web interface.
*   **Extensible & Testable:** Designed for easy expansion and robust development.

### Upcoming Features (See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md))

*   **Chord-Lyrics Synchronization:** Align extracted chords with lyrical lines for seamless learning and performance.
*   **Advanced Flourish Generation:** Incorporate deeper music theory for more sophisticated and contextually aware flourishes.
*   **Chord Substitution/Reharmonization:** Suggest alternative chords to creatively modify existing progressions.
*   **Intelligent Fingering Advisor:** Recommend optimal guitar fingerings for chords and progressions, considering ease and flow.

---

## Known Issues

*   Some dependencies (essentia, magenta, aubio) are difficult to install on Windows.
*   Chordino is not supported on Windows.
*   Large or corrupt audio files may cause extraction to fail or timeout.
*   See [GitHub Issues](https://github.com/blairmichaelg/Acoustical/issues) for up-to-date bug reports and workarounds.

## How to Add a New Backend/Plugin

Chord extraction supports plugins and fallback logic. Built-in backends (Chordino, autochord, chord-extractor) are tried in order; if all fail, registered plugins are tried in order.

1.  **Write a function** that takes `audio_path` and returns a list of `{"time": float, "chord": str}` dicts.
2.  **Register it:**
    ```python
    from chord_extraction import register_chord_extraction_backend

    def my_plugin_backend(audio_path):
        # Your extraction logic here
        return [{"time": 0.0, "chord": "X"}, {"time": 1.0, "chord": "Y"}]

    register_chord_extraction_backend(my_plugin_backend)
    ```
3.  **Test your plugin** with the CLI, web app, or `get_chords()`.

---

## Usage

### CLI

*   Run `python cli/cli.py --help` for all options and subcommands.
*   **Example commands:**
    ```bash
    # Extract chords from a local audio file
    python cli/cli.py extract-chords path/to/song.mp3

    # Extract chords from a YouTube URL
    python cli/cli.py extract-chords "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Batch extract chords from all audio files in a local directory
    python cli/cli.py extract-chords path/to/audio/directory --batch

    # Get lyrics for a song by URL
    python cli/cli.py get-lyrics --url "https://www.youtube.com/watch?v=..."

    # Get lyrics for a song by title and artist
    python cli/cli.py get-lyrics --title "Bohemian Rhapsody" --artist "Queen"

    # Transpose chords from a JSON file
    python cli/cli.py transpose chords.json --semitones +2

    # Recommend capo position
    python cli/cli.py capo chords.json

    # Generate flourishes
    python cli/cli.py flourish chords.json --magenta

    # Check backend availability
    python cli/cli.py check-backends
    ```
*   Use `--list-backends` to see available backends.
*   Use `--version` to print version info.

### Web App

*   Upload audio or paste a URL, extract chords, retrieve lyrics, transpose, capo, flourish, and download results.
*   **Chord Extraction:** Use the "Audio URL" field for direct URL input, or "Audio File" for local files.
*   **Batch Extraction:** Use the "Batch Audio Files" input to upload and process multiple local audio files at once.
*   **Lyrics Retrieval:** Use the "Audio URL" field for YouTube/Spotify links, or provide "Song Title" and "Artist" to fetch lyrics.
*   Flourish method: Choose between rule-based, Magenta, or GPT4All for flourish generation.
*   Keyboard navigation and accessibility supported.
*   Click "Report Bug / Feedback" in the footer to open a GitHub issue.

---

## API Usage

*   **Extract chords in Python (from file or URL):**
    ```python
    from chord_extraction import get_chords
    chords_from_file = get_chords("audio_input/song.mp3")
    chords_from_url = get_chords("https://www.youtube.com/watch?v=...")
    ```
*   **Batch extraction:**
    ```python
    from chord_extraction import get_chords_batch
    results = get_chords_batch(["file1.mp3", "file2.wav"])
    ```
*   **Retrieve lyrics:**
    ```python
    # Using the web app endpoint (example, actual implementation might vary)
    # This would typically be called from a frontend or another service
    import requests
    lyrics_data = requests.post("http://localhost:5000/get_lyrics", json={"url": "https://www.youtube.com/watch?v=..."}).json()
    print(lyrics_data.get("lyrics"))

    # Or directly via a Python function (future implementation)
    # from lyrics_retrieval import get_lyrics
    # lyrics = get_lyrics(url="https://www.youtube.com/watch?v=...")
    # lyrics = get_lyrics(title="Song Title", artist="Artist Name")
    ```
*   **Check backend availability:**
    ```python
    from chord_extraction import check_backend_availability
    print(check_backend_availability())
    ```

---

## Troubleshooting

*   If a backend fails, errors are logged and reported.
*   For missing dependencies, see requirements.txt and install only what you need.
*   Run `python check_backends.py` for backend diagnostics.
*   For more help, see [GitHub Issues](https://github.com/blairmichaelg/Acoustical/issues).

---

## Folder Structure

```
audio_input/                # Audio files or YouTube downloads
chord_extraction/           # Extraction modules and backend registry
key_transpose_capo/         # Key/capo logic
flourish_engine/            # Flourish/AI code
cli/                        # CLI interface
web_app/                    # Flask backend, minimal frontend
common/                     # Shared utilities (error formatting, serialization)
config.py                   # Centralized configuration
data/                       # Project files
tests/                      # Organized tests (e.g., chord_extraction/, flourish_engine/)
```

## Development & Contributing

*   Each module is documented with docstrings and sample I/O.
*   Add new extraction or flourish backends as plugins.
*   Run tests and linting with:
    ```
    make test
    make lint
    ```
*   Continuous Integration: All pushes and pull requests are tested and linted via [GitHub Actions](.github/workflows/python-app.yml).
*   See `/tests` and `/data` for examples.
*   Open a PR or issue for bugs, features, or questions.
*   Good first issues are labeled in [GitHub Issues](https://github.com/blairmichaelg/Acoustical/issues).

---

## Example JSON Output

```json
[
  {"time": 0.0, "chord": "G"},
  {"time": 2.5, "chord": "D"}
]
```

## AI Prompt Template (for AI/LLM Integration)

This template can be used to generate creative chord suggestions using an AI model:

```
Given this chord progression in key of G: [G, Em, C, D]
And these lyrics: “I walked along the riverside…”
Suggest three chord substitutions or extensions that fit mood.
```

---

## License

This project is licensed under the MIT license.
See the [LICENSE](LICENSE) file for details.

## Contact

Open issues or discussions on GitHub for support and ideas.
