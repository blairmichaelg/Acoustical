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

# Model path should be sourced from config.py or environment variable
try:
    from config import GPT4ALL_MODEL_PATH as DEFAULT_MODEL_PATH
except ImportError:
    log.warning("GPT4ALL_MODEL_PATH not found in config.py. GPT4All functionality might be limited if path not provided.")
    DEFAULT_MODEL_PATH = None


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
    if not actual_model_path:
        log.error("GPT4All model path is not configured. Cannot load model.")
        results = []
        for chord_obj in chord_progression:
            c = chord_obj.get("chord", "N/A")
            results.append({
                "original_chord": c,
                "start_time": chord_obj.get("time"),
                "suggestions": [f"{c}7", f"{c}add9"] if c != "N/A" else [] 
            })
        return results
        
    try:
        log.info(f"Attempting to load GPT4All model from: {actual_model_path}")
        model = GPT4All(actual_model_path)
        log.info("GPT4All model loaded successfully.")
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

        try:
            with model.chat_session():
                response = model.generate(
                    prompt, max_tokens=max_tokens, temp=0.7, top_k=40, top_p=0.9
                )

            text_to_parse = response.strip()
            
            # 1. Remove global introductory phrases iteratively
            global_intro_phrases = [
                "Sure, here are some suggestions:", "Here's a suggestion:", 
                "Okay, how about" 
            ]
            active_text = text_to_parse
            made_change_in_pass = True
            while made_change_in_pass:
                made_change_in_pass = False
                for phrase in global_intro_phrases:
                    match = re.match(f"^{re.escape(phrase)}\s*[:,]?\s*", active_text, re.IGNORECASE)
                    if match:
                        active_text = active_text[match.end():].strip()
                        made_change_in_pass = True
                        break 
            text_to_parse = active_text
            
            # 2. Normalize conjunctions and primary delimiters (newline, comma) to a single unique delimiter (e.g., pipe)
            text_to_parse = re.sub(r'\s+(?:or|and)\s+', '|', text_to_parse, flags=re.IGNORECASE)
            text_to_parse = re.sub(r'[\n\r\t,]+', '|', text_to_parse) # Newlines and commas to pipe
            text_to_parse = re.sub(r'[|]+', '|', text_to_parse) # Consolidate multiple pipes
            
            # Now split by the pipe. Then, each part might still contain space-separated chords.
            parts_from_pipe_split = text_to_parse.split('|')
            
            potential_suggestions_final = []
            for part in parts_from_pipe_split:
                # Split parts that might be space-separated chords, e.g., "C G Am"
                space_separated_sub_parts = re.split(r'\s+', part.strip())
                potential_suggestions_final.extend(p for p in space_separated_sub_parts if p)

            cleaned_suggestions = set()
            item_intro_phrases = ["Try", "Maybe", "Consider", "Perhaps", "How about", "What about", "An option is", "Another option is", "Or perhaps"] 
            trailing_punctuation = ".?!\"'"
            
            for part_to_clean in potential_suggestions_final: # Iterate over the fully split parts
                s_processed = part_to_clean.strip()
                if not s_processed: continue

                # 3. Remove item-specific leading phrases iteratively for each part
                active_s_part = s_processed
                made_item_change = True
                while made_item_change:
                    made_item_change = False
                    original_len = len(active_s_part)
                    for phrase in item_intro_phrases:
                        match = re.match(f"^{re.escape(phrase)}\s*[:,]?\s*", active_s_part, re.IGNORECASE)
                        if match:
                            active_s_part = active_s_part[match.end():].strip()
                            if len(active_s_part) < original_len:
                                made_item_change = True
                            break 
                    if not made_item_change: # No phrase removed in this pass for this item
                        break
                s_processed = active_s_part

                # 4. Remove common trailing punctuation
                if s_processed and s_processed[-1] in trailing_punctuation:
                    s_processed = s_processed[:-1].strip()
                
                # 5. Validate with regex
                chord_pattern = r"^[A-G][#b]?([\w\d#b\+\-\(\)]*)(/([A-G][#b]?))?$"
                if s_processed and re.fullmatch(chord_pattern, s_processed, re.IGNORECASE):
                    cleaned_suggestions.add(s_processed)
                elif s_processed: 
                    log.debug(f"Filtered out potential non-chord suggestion: '{s_processed}' from original part: '{part_to_clean}'")

            if not cleaned_suggestions and current_chord_str: 
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
                "suggestions": [f"{current_chord_str}sus", f"{current_chord_str}6"]
            })

    return llm_results

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
