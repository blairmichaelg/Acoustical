"""
Common utilities for error formatting and result serialization.
"""

import json
import logging
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)


def handle_exception(
    e: Exception, message: str = "An unexpected error occurred"
) -> Dict[str, str]:
    """
    Logs an exception with a custom message and returns a standardized error dictionary.
    """
    log.exception(f"{message}: {e}")
    return {"error": f"{message}: {e}"}


def format_error(message: str, exc: Optional[Exception] = None) -> Dict[str, str]:
    """
    Formats an error message, optionally including an exception.

    Logs the error and returns a dictionary with an "error" key.

    Args:
        message (str): The primary error message.
        exc (Optional[Exception]): The exception object, if any.

    Returns:
        Dict[str, str]: A dictionary containing the formatted error message.
    """
    if exc:
        return handle_exception(exc, message)
    else:
        log.error(message)
        return {"error": message}


def serialize_result(result: Any) -> str:
    """
    Serializes a result to a JSON string.

    Args:
        result (Any): The data to serialize.

    Returns:
        str: The JSON string representation of the result.
             If serialization fails, returns a JSON string with an error message.
    """
    try:
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_exception(e, "Serialization failed")
