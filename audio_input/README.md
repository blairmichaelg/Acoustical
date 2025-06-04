# Audio Input Directory

This directory is used to store audio files for processing by the Acoustic Cover Assistant.

## Contents

*   **Sample Audio Files:** Place `.mp3`, `.wav`, `.flac`, or other supported audio files here for local chord extraction and testing.
*   **Downloaded Audio:** When using the web app or CLI to extract chords from a URL, audio files will be temporarily downloaded to a temporary directory managed by the application, not directly into this folder. This directory is primarily for user-provided local files or for development/testing purposes.

## Usage

*   **Local Files:** To process a local audio file, place it in this directory (or any other accessible path) and provide its path to the CLI or upload it via the web app.
*   **URL Input:** For seamless processing of audio from YouTube or other online sources, simply provide the URL directly to the chord extraction feature in the web app or CLI. The application will handle the temporary download.
