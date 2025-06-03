# Poetry/Pipenv Evaluation

## Poetry
- Modern dependency management and packaging tool for Python.
- Handles optional dependencies, lock files, and virtual environments.
- Recommended for projects with complex or optional dependencies (like this one).
- See: https://python-poetry.org/docs/

## Pipenv
- User-friendly dependency manager with Pipfile and lock support.
- Good for simple projects, but less flexible than Poetry for advanced use cases.
- See: https://pipenv.pypa.io/en/latest/

## Recommendation
- For this project, Poetry is recommended for its robust handling of optional and platform-specific dependencies.
- Migration steps:
  1. Install Poetry: `pip install poetry`
  2. Run `poetry init` and follow prompts.
  3. Add dependencies: `poetry add <package>`
  4. Add optional dependencies with `--optional`.
  5. Use `poetry install` and `poetry run` for environment management.

# See README for more details.
