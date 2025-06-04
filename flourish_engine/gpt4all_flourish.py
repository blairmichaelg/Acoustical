import logging
import re # Added re import
from typing import List, Dict, Any, Optional

from key_transpose_capo.key_analysis import detect_key_from_chords
from music_theory import utils as music_theory_utils

try:
    from gpt4all import GPT4All
    _gpt4all_available = True
except ImportError:
    _gpt4all_available = False
    GPT4All = None  # Define GPT4All as None if import fails

log = logging.getLogger(__name__)

# Ensure this path is correct or make it configurable
DEFAULT_MODEL_PATH = "c:\\Users\\Michael\\acoustical\\ggml-gpt4all-j-v1.3-groovy.bin"


def suggest_chord_substitutions(
    chord_progression: List[Dict[str, Any]],
    lyrics: Optional[str] = None,
    model_path: Optional[str] = None,
    max_tokens: int = 50  # Reduced for more concise suggestions
) -> List[Dict[str, Any]]:
    """
    Suggest chord substitutions/extensions using GPT4All, with music theory context.
    Falls back to static suggestions if GPT4All is not installed or fails.

    Args:
        chord_progression (List[Dict[str, Any]]): List of chord objects,
            each with "chord" (str) and "time" (float) keys.
        lyrics (str, optional): Associated lyrics for context.
        model_path (str, optional): Path to GPT4All model file.
        max_tokens (int): Max tokens to generate per suggestion.

    Returns:
        List[Dict[str, Any]]: A list of suggestions for each original chord.
            Each item: {"original_chord": str, "start_time": float, "suggestions": List[str]}
    """
    if not _gpt4all_available or GPT4All is None:
        log.warning("GPT4All is not installed. Returning static suggestions.")
        results = []
        for chord_obj in chord_progression:
            c = chord_obj.get("chord", "N/A")
            results.append({
                "original_chord": c,
                "start_time": chord_obj.get("time"),
                "suggestions": [f"{c}maj7", f"{c}9"] if c != "N/A" else []
            })
        return results

    actual_model_path = model_path or DEFAULT_MODEL_PATH
    try:
        model = GPT4All(actual_model_path)
    except Exception as e:
        log.error(f"Failed to load GPT4All model from {actual_model_path}: {e}")
        results = []
        for chord_obj in chord_progression:
            c = chord_obj.get("chord", "N/A")
            results.append({
                "original_chord": c,
                "start_time": chord_obj.get("time"),
                "suggestions": [f"{c}7", f"{c}add9"] if c != "N/A" else []
            })
        return results

    # Detect overall key for context
    original_chord_strings = [c.get("chord", "") for c in chord_progression]
    detected_key_info = detect_key_from_chords(original_chord_strings)
    key_root_str = detected_key_info.get("key_root")
    key_quality_str = detected_key_info.get("key_quality", "major")

    key_context_prompt = ""
    if key_root_str:
        key_context_prompt = (
            f"The song is likely in the key of {key_root_str} {key_quality_str}. "
        )
        key_scale_notes = music_theory_utils.generate_scale(key_root_str, key_quality_str)
        if key_scale_notes:
            key_context_prompt += f"The notes in this key are: {', '.join(key_scale_notes)}. "

    llm_results = []
    for chord_obj in chord_progression:
        current_chord_str = chord_obj.get("chord")
        if not current_chord_str:
            llm_results.append({
                "original_chord": "N/A",
                "start_time": chord_obj.get("time"),
                "suggestions": []
            })
            continue

        prompt = (
            f"{key_context_prompt}"
            f"Given the chord '{current_chord_str}', suggest one or two musically "
            f"interesting and common chord substitutions or extensions (like adding a "
            f"7th, 9th, sus, or a related minor/major chord). "
            f"Be concise. Examples: G7, Am7, Csus4. "
        )
        # Consider removing lyrics or making it a very optional, light context
        # if lyrics:
        #     prompt += f"Consider the lyrical context if relevant: \"{lyrics[:50]}...\""

        try:
            # Using a context manager for the chat session is good practice
            with model.chat_session():
                response = model.generate(
                    prompt, max_tokens=max_tokens, temp=0.7, top_k=40, top_p=0.9
                )

            # Basic response cleaning
            raw_suggestions = response.strip().replace("Sure, here are some suggestions:", "")
            raw_suggestions = raw_suggestions.replace("Here's a suggestion:", "")
            potential_suggestions = re.split(r'[,\n\r\t\.\-]| or | and ', raw_suggestions)

            cleaned_suggestions = set()
            for s in potential_suggestions:
                s_cleaned = s.strip()
                # Regex to match common chord patterns (simplistic but better than nothing)
                if s_cleaned and re.match(
                    r"^[A-G][#b]?(maj|m|min|dim|aug|sus|add|\d)*[#b\d]*$",
                    s_cleaned,
                    re.IGNORECASE
                ):
                    cleaned_suggestions.add(s_cleaned)

            if not cleaned_suggestions and current_chord_str: # Fallback
                cleaned_suggestions.add(current_chord_str)


            llm_results.append({
                "original_chord": current_chord_str,
                "start_time": chord_obj.get("time"),
                "suggestions": sorted(list(cleaned_suggestions))
            })
        except Exception as e:
            log.error(f"GPT4All generation failed for '{current_chord_str}': {e}")
            llm_results.append({
                "original_chord": current_chord_str,
                "start_time": chord_obj.get("time"),
                "suggestions": [f"{current_chord_str}sus", f"{current_chord_str}6"]  # Fallback
            })

    return llm_results


# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if _gpt4all_available:
        print("GPT4All is available. Running example...")
        test_prog = [
            {"chord": "C", "time": 0.0},
            {"chord": "G", "time": 2.0},
            {"chord": "Am", "time": 4.0},
            {"chord": "F", "time": 6.0}
        ]
        suggestions = suggest_chord_substitutions(test_prog)
        for item in suggestions:
            print(
                f"Original: {item['original_chord']} (at {item['start_time']}), "
                f"LLM Suggestions: {item['suggestions']}"
            )
    else:
        print("GPT4All is not available. Skipping LLM example.")
