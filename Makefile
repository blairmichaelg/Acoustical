.PHONY: test lint format check-backends coverage dev clean

test:
	pytest

lint:
	flake8 .
	mypy .

format:
	black .

check-backends:
	python check_backends.py

coverage:
	pytest --cov=.

dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

clean:
	rm -rf __pycache__
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.pytest_cache' -delete
