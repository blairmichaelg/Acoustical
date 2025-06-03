# Acoustic Cover Assistant

![CI](https://github.com/TODO-REPLACE-WITH-USERNAME/TODO-REPLACE-WITH-REPONAME/actions/workflows/python-app.yml/badge.svg)

A modular, open-source pipeline for extracting chords, analyzing key, transposing, recommending capo positions, and generating musical flourishes from audio. Includes CLI and minimal web interface.

> **Note:** Replace all TODO-REPLACE-WITH-USERNAME/REPONAME with your actual GitHub repository info.

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

1. **Clone the repo and create a Python 3.11+ virtual environment.**
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
   For advanced features (audio analysis, flourishes), uncomment optional lines in requirements.txt or use Poetry/Pipenv.
3. **Run tests:**
   ```
   make test
   ```
4. **Start the web app:**
   ```
   python web_app/app.py
   ```
   Open your browser at [http://localhost:5000](http://localhost:5000)

---

## Features

- Chord extraction from audio (Chordino, autochord, chord-extractor)
- Key detection and transposition (music21)
- Capo recommendation based on chord complexity
- Flourish generation (rule-based, Magenta, GPT4All)
- CLI and web app interfaces
- Extensible, testable, and AI-friendly

## Known Issues

- Some dependencies (essentia, magenta, aubio) are difficult to install on Windows.
- Chordino is not supported on Windows.
- Large or corrupt audio files may cause extraction to fail or timeout.
- See [GitHub Issues](https://github.com/TODO-REPLACE-WITH-USERNAME/TODO-REPLACE-WITH-REPONAME/issues) for up-to-date bug reports and workarounds.

## How to Add a New Backend/Plugin

Chord extraction supports plugins and fallback logic. Built-in backends (Chordino, autochord, chord-extractor) are tried in order; if all fail, registered plugins are tried in order.

1. **Write a function** that takes `audio_path` and returns a list of `{"time": float, "chord": str}` dicts.
2. **Register it:**
   ```python
   from chord_extraction import register_chord_extraction_backend

   def my_plugin_backend(audio_path):
       # Your extraction logic here
       return [{"time": 0.0, "chord": "X"}, {"time": 1.0, "chord": "Y"}]

   register_chord_extraction_backend(my_plugin_backend)
   ```
3. **Test your plugin** with the CLI, web app, or `get_chords()`.

---

## Usage

### CLI

- Run `python cli/cli.py --help` for all options and subcommands.
- Example commands:
  ```
  python cli/cli.py extract-chords path/to/song.mp3
  python cli/cli.py extract-chords path/to/dir --batch
  python cli/cli.py transpose chords.json --semitones +2
  python cli/cli.py capo chords.json
  python cli/cli.py flourish chords.json --magenta
  python cli/cli.py check-backends
  ```
- Batch extraction: `python cli/cli.py extract-chords path/to/dir --batch` will process all audio files in the directory.
- Use `--list-backends` to see available backends.
- Use `--version` to print version info.

### Web App

- Upload audio or chord JSON, extract/transpose/capo/flourish, and download results.
- Batch extraction: Use the "Batch Audio Files" input to upload and process multiple audio files at once.
- Flourish method: Choose between rule-based, Magenta, or GPT4All for flourish generation.
- Keyboard navigation and accessibility supported.
- Click "Report Bug / Feedback" in the footer to open a GitHub issue.


---

## API Usage

- **Extract chords in Python:**
  ```python
  from chord_extraction import get_chords
  chords = get_chords("audio_input/song.mp3")
  ```
- **Batch extraction:**
  ```python
  from chord_extraction import get_chords_batch
  results = get_chords_batch(["file1.mp3", "file2.wav"])
  ```
- **Check backend availability:**
  ```python
  from chord_extraction import check_backend_availability
  print(check_backend_availability())
  ```

---

## Troubleshooting

- If a backend fails, errors are logged and reported.
- For missing dependencies, see requirements.txt and install only what you need.
- Run `python check_backends.py` for backend diagnostics.
- For more help, see [GitHub Issues](https://github.com/TODO-REPLACE-WITH-USERNAME/TODO-REPLACE-WITH-REPONAME/issues).

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

- Each module is documented with docstrings and sample I/O.
- Add new extraction or flourish backends as plugins.
- Run tests and linting with:
  ```
  make test
  make lint
  ```
- Continuous Integration: All pushes and pull requests are tested and linted via [GitHub Actions](.github/workflows/python-app.yml).
- See `/tests` and `/data` for examples.
- Open a PR or issue for bugs, features, or questions.
- Good first issues are labeled in [GitHub Issues](https://github.com/yourusername/yourrepo/issues).

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

This project is licensed under the TODO-REPLACE-WITH-LICENSE-TYPE license.
See the [LICENSE](LICENSE) file for details.

## Contact

Open issues or discussions on GitHub for support and ideas.
