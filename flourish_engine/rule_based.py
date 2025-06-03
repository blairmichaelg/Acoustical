"""
Rule-based chord substitutions and flourishes.
"""
import logging
from typing import List, Dict, Any
from config import RULE_BASED_SUBSTITUTIONS
from key_transpose_capo.key_analysis import detect_key_from_chords
from music21 import harmony, pitch, interval, key as m21key # Import key explicitly

log = logging.getLogger(__name__)

def apply_rule_based_flourishes(chords: List[str], rule_set_name: str = "default") -> List[str]:
    """
    Apply rule-based chord substitutions and flourishes to a progression.

    This function applies predefined substitution rules based on the detected key
    and chord context.

    Args:
        chords (List[str]): List of chord names as strings.
        rule_set_name (str): Name of the predefined rule set to use (e.g., "default", "simplify", "jazz", "blues").
                             Defaults to "default".

    Returns:
        List[str]: List of chords after applying flourishes.

    Raises:
        ValueError: If the specified rule_set_name is not found.
        RuntimeError: If key detection fails.
    """
    try:
        # Get the substitution dictionary for the rule set
        substitutions = RULE_BASED_SUBSTITUTIONS.get(rule_set_name)
        if substitutions is None:
             raise ValueError(f"Rule set '{rule_set_name}' not found.")
    except KeyError: # Should not happen with .get() but keep for safety
        raise ValueError(f"Rule set '{rule_set_name}' not found. Available sets: {list(RULE_BASED_SUBSTITUTIONS.keys())}")

    # Detect the key of the progression
    try:
        key_str = detect_key_from_chords(chords)
        # Parse the key string into a music21 Key object
        # Use m21key.Key instead of harmony.Key
        key = m21key.Key(key_str)
        log.info(f"Detected key: {key_str}")
    except Exception as e:
        log.warning(f"Failed to detect key for flourish application: {e}. Context-aware rules may not apply.")
        key = None # Proceed without key context

    flourished_chords = []
    for i, current_chord_str in enumerate(chords):
        # Apply simple 1-to-1 substitutions first
        substituted_chord_str = substitutions.get(current_chord_str, current_chord_str)

        # Apply context-aware rules (example: V to V7 in major keys)
        # This is a simplified example and needs more sophisticated music21 logic
        if key and substituted_chord_str == current_chord_str: # Only apply if no simple substitution occurred
            try:
                current_chord_m21 = harmony.ChordSymbol(substituted_chord_str)
                # Check if the current chord is the dominant (V) chord in the detected key
                # This requires comparing the root of the chord to the dominant pitch of the key
                dominant_pitch = key.getDominant().pitch
                if current_chord_m21.root().name == dominant_pitch.name and key.mode == 'major':
                     # If it's a major triad V, change it to a dominant 7th
                     if current_chord_m21.quality == 'major' and len(current_chord_m21.pitches) == 3:
                          # A more robust music21 approach would be needed here
                          # For now, a simple string append as a placeholder
                          substituted_chord_str = current_chord_str + "7"
                          log.debug(f"Applied V to V7 rule to {current_chord_str} in key {key_str}")
            except Exception as e:
                 log.warning(f"Failed to apply context rule for chord {current_chord_str}: {e}")

        flourished_chords.append(substituted_chord_str)

    return flourished_chords
