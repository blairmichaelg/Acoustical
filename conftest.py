import sys
import os

# Add the project root directory to the Python path
# This allows pytest to find main application modules (e.g., audio_input)
# when running tests from subdirectories.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
