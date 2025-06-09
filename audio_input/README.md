# Audio Input Directory

This directory is used to store audio files for processing by the Acoustic Cover Assistant.

## Contents

*   **Sample Audio Files:** Place `.mp3`, `.wav`, `.flac`, or other supported audio files (see project configuration for a full list) here for local chord extraction and testing.
*   **Downloaded Audio:** The `audio_input/downloader.py` script, by default, saves downloaded audio into this `audio_input` directory (or a specified output path). The web application might use a system temporary directory for downloads. This `audio_input` directory can serve as a default location for downloaded files or for user-provided local files.

## Usage

*   **Local Files:** To process a local audio file, you can place it in this directory and provide its path (e.g., `audio_input/my_song.mp3`) to the CLI, or upload it via the web app.
*   **URL Input:** When providing a URL (e.g., YouTube) to the CLI's download command or the web app, the audio will be downloaded. The CLI's download command defaults to saving in this `audio_input` directory unless a different output directory is specified.
