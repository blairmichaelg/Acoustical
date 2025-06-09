"""
Audio file utilities for validation and preprocessing.
"""

import os
import mimetypes
from typing import Set

from config import ALLOWED_AUDIO_EXTENSIONS as ALLOWED_EXTENSIONS, MAX_AUDIO_FILE_SIZE_MB as MAX_FILE_SIZE_MB

def is_allowed_audio_file(filename: str) -> bool:
    """
    Checks if the file extension is in the list of allowed audio extensions.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the extension is allowed, False otherwise.
    """
    ext = os.path.splitext(filename)[-1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_valid_audio_mime(filename: str) -> bool:
    """
    Checks if the file's MIME type indicates an audio file.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the MIME type is audio, False otherwise.
    """
    mime, _ = mimetypes.guess_type(filename)
    return mime is not None and mime.startswith("audio")

def is_file_size_ok(filepath: str, max_mb: int = MAX_FILE_SIZE_MB) -> bool:
    """
    Checks if the file size is within the allowed limit.

    Args:
        filepath (str): The path to the file.
        max_mb (int): The maximum allowed file size in megabytes.

    Returns:
        bool: True if the file size is within the limit, False otherwise.
    """
    if not os.path.exists(filepath):
        # Cannot check size if file doesn't exist, assume not ok for size check purpose
        return False
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    return size_mb <= max_mb

def check_audio_file(filepath: str) -> bool:
    """
    Checks if the file is a valid, allowed audio file and not too large.

    Performs checks for file existence, allowed extension, valid MIME type,
    and file size limit.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if all checks pass.

    Raises:
        ValueError: With a descriptive message if any check fails.
    """
    if not os.path.isfile(filepath):
        raise ValueError(f"File does not exist: {filepath}")
    if not is_allowed_audio_file(filepath):
        # Sort extensions for consistent error message
        sorted_extensions = sorted(list(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported file type: {filepath}. Allowed types: {', '.join(sorted_extensions)}")
    if not is_valid_audio_mime(filepath):
        raise ValueError(f"Invalid audio MIME type for file: {filepath}")
    if not is_file_size_ok(filepath):
        raise ValueError(f"File too large (>{MAX_FILE_SIZE_MB} MB): {filepath}")
    # Optionally: add more checks for corruption or decoding here
    return True
