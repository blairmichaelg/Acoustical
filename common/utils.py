"""
Common utilities for error formatting and result serialization.
"""

import json
import logging
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)

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
        log.error(f"{message}: {exc}", exc_info=True) # Log traceback
        return {"error": f"{message}: {exc}"}
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
        log.error(f"Serialization failed: {e}", exc_info=True)
        # Return a JSON string containing an error dictionary
        return json.dumps({"error": f"Serialization failed: {e}"})
