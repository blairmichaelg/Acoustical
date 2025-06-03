# Contributing to Acoustic Cover Assistant

Thank you for your interest in contributing! Please read these guidelines to help us maintain a high-quality, welcoming project.

## Getting Started

- Fork the repository and create a feature branch (use `main` as the base branch).
- Install dependencies with `pip install -r requirements.txt` (or use Poetry/Pipenv if preferred).
- Run tests with `pytest` before submitting a PR.
- For web/frontend changes, test accessibility and cross-browser compatibility.
- To run the web app locally:  
  ```
  python web_app/app.py
  ```
  Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Coding Standards

- Use clear, descriptive variable and function names.
- Write docstrings for all public functions and modules.
- Follow PEP8 for Python code. Use `black` or `flake8` for formatting/linting.
- Run linting with:
  ```
  make lint
  ```
  or
  ```
  flake8 .
  ```
- Keep code modular and testable. Add/expand tests for new features or bugfixes.
- For web UI, use semantic HTML and ensure accessibility (aria-labels, color contrast, keyboard navigation).

## Testing

Run tests with:
```
pytest
```

### Test Organization
Tests are organized by module:
- `tests/chord_extraction/`: Chord extraction backends and integration tests.
- `tests/flourish_engine/`: Flourish generation tests.
- `tests/test_downloader.py`: Audio downloader tests.

### Adding Tests
- Add tests for new features or bugfixes.
- Use descriptive test names and include edge cases.
- Mock external dependencies (e.g., yt-dlp, subprocess) where needed.

## Configuration

The project uses a centralized configuration file (`config.py`) for settings like:
- Default output formats.
- Backend preferences.
- Audio file size limits.

Update `config.py` for global changes, and ensure modules use these settings instead of hardcoding values.

## Pull Requests

- Reference related issues in your PR description.
- Include a summary of changes and testing steps.
- Ensure all tests pass and CI is green.
- Update documentation and sample data as needed.

## Reporting Bugs & Feedback

- Use GitHub Issues for bugs and feature requests.
- For regressions, include sample data and steps to reproduce.
- For accessibility or UI issues, include browser/OS details.

## Code of Conduct

- Be respectful and constructive in all interactions.
- See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

---

Happy contributing!
