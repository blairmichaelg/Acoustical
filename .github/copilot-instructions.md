<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

- This project is a modular Python-based acoustic-cover assistant.
- Use music21 for music theory and transposition, aubio for chord extraction and audio analysis (default backend on Windows), and Magenta for AI flourishes.
- Essentia is optional and may require manual install or WSL; code should gracefully handle its absence.
- CLI is built with Click, web app with Flask.
- Folder structure is modular: see README.md for details.
- Prioritize cross-platform compatibility, clear error messages, and testable code.
