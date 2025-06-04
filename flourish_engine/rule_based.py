import logging
from typing import List, Dict, Any # Removed Optional

from config import RULE_BASED_SUBSTITUTIONS
from key_transpose_capo.key_analysis import detect_key_from_chords
from music_theory import utils as music_theory_utils

log = logging.getLogger(__name__)


def apply_rule_based_flourishes(
    chord_progression: List[Dict[str, Any]],
    rule_set_name: str = "default"
) -> List[Dict[str, Any]]:
    """
    Apply rule-based chord substitutions and flourishes to a progression.
    Integrates music_theory.utils for more musically aware suggestions.

    Args:
        chord_progression (List[Dict[str, Any]]): List of chord objects,
            each with at least "chord" (str) and "time" (float) keys.
        rule_set_name (str): Name of the predefined rule set to use.

    Returns:
        List[Dict[str, Any]]: A list of flourish suggestions for each original chord.
            Each item is a dict: {"original_chord": str, "start_time": float, "suggestions": List[str]}
    """
    try:
        substitutions_config = RULE_BASED_SUBSTITUTIONS.get(rule_set_name, {})
        if rule_set_name not in RULE_BASED_SUBSTITUTIONS and rule_set_name != "default":
            log.warning(f"Rule set '{rule_set_name}' not found. Using default rules.")
    except Exception as e:
        log.error(f"Error loading rule set '{rule_set_name}': {e}. Using empty rules.")
        substitutions_config = {}

    original_chord_strings = [c.get("chord", "") for c in chord_progression]
    detected_key_info = detect_key_from_chords(original_chord_strings)
    key_root_str = detected_key_info.get("key_root")
    key_quality_str = detected_key_info.get("key_quality", "major")  # Default to major

    log.info(f"Detected key for flourishes: {key_root_str} {key_quality_str}")

    flourish_results = []

    for i, current_chord_obj in enumerate(chord_progression):
        current_chord_str = current_chord_obj.get("chord")
        if not current_chord_str:
            continue

        suggestions = {current_chord_str}  # Use a set for unique suggestions

        # 1. Simple 1-to-1 substitutions from config
        simple_sub_rules = substitutions_config.get("simple_substitutions", {})
        simple_sub = simple_sub_rules.get(current_chord_str)
        if simple_sub:
            suggestions.add(simple_sub)

        # 2. Music theory-based suggestions
        if key_root_str:
            key_scale_notes = music_theory_utils.generate_scale(key_root_str, key_quality_str)
            parsed_notes = music_theory_utils.parse_chord_to_notes(current_chord_str)

            if parsed_notes and len(parsed_notes) >= 3:  # Is at least a triad
                root_val = music_theory_utils.get_note_value(parsed_notes[0])
                if root_val is not None:
                    # Rule: Suggest adding diatonic 7th
                    m7_interval_val = (root_val + 10) % 12
                    m7_note_name = music_theory_utils.get_note_name(m7_interval_val)
                    if m7_note_name in key_scale_notes:
                        if "m" in current_chord_str or "min" in current_chord_str:
                            suggestions.add(
                                current_chord_str.replace("m", "m7", 1).replace("min", "min7", 1)
                            )
                        elif "dim" not in current_chord_str and "aug" not in current_chord_str:
                            suggestions.add(current_chord_str + "7")  # Dominant 7th

                    M7_interval_val = (root_val + 11) % 12
                    M7_note_name = music_theory_utils.get_note_name(M7_interval_val)
                    if M7_note_name in key_scale_notes:
                        is_plain_major = not any(
                            q in current_chord_str for q in ["m", "min", "dim", "aug", "7"]
                        )
                        if "maj" in current_chord_str or "M" in current_chord_str or is_plain_major:
                            suggestions.add(current_chord_str + "maj7")

            # Rule: Suggest sus4 / sus2 if applicable
            is_sus_dim_aug = "sus" in current_chord_str or \
                             "dim" in current_chord_str or \
                             "aug" in current_chord_str
            if not is_sus_dim_aug:
                suggestions.add(current_chord_str + "sus4")
                suggestions.add(current_chord_str + "sus2")

        # Rule: Passing diminished chord (simplified)
        if i + 1 < len(chord_progression):
            next_chord_str = chord_progression[i+1].get("chord")
            if next_chord_str and current_chord_str: # Ensure both exist
                current_parsed = music_theory_utils.parse_chord_to_notes(current_chord_str)
                next_parsed = music_theory_utils.parse_chord_to_notes(next_chord_str)

                if current_parsed and next_parsed:
                    current_root_val = music_theory_utils.get_note_value(current_parsed[0])
                    next_root_val = music_theory_utils.get_note_value(next_parsed[0])

                    if current_root_val is not None and next_root_val is not None:
                        # Whole step up to next chord
                        if (next_root_val - current_root_val + 12) % 12 == 2:
                            passing_dim_root_val = (current_root_val + 1) % 12
                            passing_dim_root_name = music_theory_utils.get_note_name(
                                passing_dim_root_val
                            )
                            suggestions.add(passing_dim_root_name + "dim")

        flourish_results.append({
            "original_chord": current_chord_str,
            "start_time": current_chord_obj.get("time"),
            "suggestions": sorted(list(suggestions))
        })

    log.info(f"Applied rule-based flourishes. Results: {len(flourish_results)} items.")
    return flourish_results


# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_progression_c_major = [
        {"chord": "C", "time": 0.0},
        {"chord": "G", "time": 2.0},
        {"chord": "Am", "time": 4.0},
        {"chord": "F", "time": 6.0}
    ]
    print("\n--- C Major Test ---")
    results_c = apply_rule_based_flourishes(test_progression_c_major)
    for res_c in results_c:
        print(
            f"Original: {res_c['original_chord']} (at {res_c['start_time']}), "
            f"Suggestions: {res_c['suggestions']}"
        )

    test_progression_a_minor = [
        {"chord": "Am", "time": 0.0},
        {"chord": "Dm", "time": 2.0},
        {"chord": "E", "time": 4.0},  # E should become E7 in Am (dominant of Am)
        {"chord": "Am", "time": 6.0}
    ]
    print("\n--- A Minor Test ---")
    results_am = apply_rule_based_flourishes(test_progression_a_minor)
    for res_am in results_am:
        print(
            f"Original: {res_am['original_chord']} (at {res_am['start_time']}), "
            f"Suggestions: {res_am['suggestions']}"
        )

    test_progression_g_major = [
        {"chord": "G", "time": 0.0},
        {"chord": "C", "time": 2.0}, # C is IV
        {"chord": "D", "time": 4.0}, # D is V
        {"chord": "G", "time": 6.0}
    ]
    print("\n--- G Major Test ---")
    results_g = apply_rule_based_flourishes(test_progression_g_major)
    for res_g in results_g:
        print(
            f"Original: {res_g['original_chord']} (at {res_g['start_time']}), "
            f"Suggestions: {res_g['suggestions']}"
        )
