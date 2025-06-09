import logging
from typing import List, Dict, Any  # Removed Tuple as it's not directly used
# import difflib # Not used yet

log = logging.getLogger(__name__)


def align_chords_with_lyrics(
    chords: List[Dict[str, Any]], lyrics_text: str
) -> List[Dict[str, Any]]:
    """
    Aligns chords with lyrical lines or sections based on heuristics.
    This implementation attempts a more realistic time-based distribution.

    Args:
        chords (List[Dict[str, Any]]): A list of dictionaries, each with "time" and "chord" keys.
        lyrics_text (str): The full lyrics as a single string.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each entry represents a lyrical line
                              or section, with associated chords.
                              Example: [{"line": "Verse 1 lyrics...", "chords": [{"time": 0.0, "chord": "C"}]}, ...]
    """
    log.info("Attempting to align chords with lyrics using time-based heuristics.")

    lines = [line.strip() for line in lyrics_text.strip().split('\n') if line.strip()]
    if not lines:
        return []

    aligned_data = [{"line": line, "chords": []} for line in lines]

    # Estimate total duration from chords if available, otherwise assume a default
    total_duration = 0.0
    if chords:
        # Assuming chords are sorted by time and the last chord's time is indicative of song end
        total_duration = chords[-1].get("time", 0.0) + 5.0  # Add a buffer

    if total_duration == 0.0:
        # Fallback if no time info in chords, assume 5 seconds per line
        total_duration = len(lines) * 5.0

    time_per_line = total_duration / len(lines) if len(lines) > 0 else 0.0
    current_chord_index = 0

    for i, line_data in enumerate(aligned_data):
        line_start_time = i * time_per_line
        line_end_time = (i + 1) * time_per_line

        # Assign chords whose timestamps fall within this line's estimated time window
        while current_chord_index < len(chords) and \
              chords[current_chord_index].get("time", 0.0) < line_end_time:

            # Only add chord if its time is within or after the line's start time
            if chords[current_chord_index].get("time", 0.0) >= line_start_time:
                line_data["chords"].append(chords[current_chord_index])

            current_chord_index += 1

    log.info(f"Aligned {len(chords)} chords with {len(lines)} lyrical lines "
             "based on estimated timing.")
    return aligned_data


def identify_song_structure(
    lyrics_text: str, chords: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Identifies basic song structure (e.g., verse, chorus, bridge) based on lyrical patterns.
    Future improvements could involve repetition analysis of chord progressions.

    Args:
        lyrics_text (str): The full lyrics as a single string.
        chords (List[Dict[str, Any]]): The extracted chords (used for timing).

    Returns:
        Dict[str, Any]: A dictionary representing the song structure.
                        Example: {"structure": [{"type": "Verse 1", "start_time": 0.0}, ...]}
    """
    log.info("Attempting to identify song structure based on lyrical patterns.")

    structure = []
    lines = [line.strip() for line in lyrics_text.strip().split('\n') if line.strip()]

    # Estimate total duration from chords if available, otherwise assume a default
    total_duration = 0.0
    if chords:
        total_duration = chords[-1].get("time", 0.0) + 5.0  # Add a buffer

    if total_duration == 0.0:
        total_duration = len(lines) * 5.0

    time_per_line = total_duration / len(lines) if len(lines) > 0 else 0.0

    section_keywords = {
        "verse": ["verse", "1st verse", "2nd verse", "third verse"],
        "chorus": ["chorus", "pre-chorus", "post-chorus"],
        "bridge": ["bridge"],
        "intro": ["intro", "introduction"],
        "outro": ["outro", "fade out"],
        "solo": ["solo", "guitar solo", "instrumental"]
    }

    section_counter = {"verse": 0, "chorus": 0, "bridge": 0, "intro": 0, "outro": 0, "solo": 0}
    # No need for potential_sections with the new direct iteration logic

    last_added_line_index = -1 # To avoid adding multiple sections for multi-line keyword phrases

    for i, line in enumerate(lines):
        if i <= last_added_line_index: # If this line was part of a multi-line keyword phrase already processed
            continue

        line_lower = line.lower()
        detected_section_type = None
        
        # Check for keywords. Order might matter if a line could match multiple types.
        # A simple priority could be intro/outro > chorus > verse > bridge > solo
        # For now, using the dict order of section_keywords.
        for sec_type, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in line_lower:
                    detected_section_type = sec_type
                    # Potentially advance last_added_line_index if keyword spans multiple lines
                    # (e.g. "guitar\nsolo"). For now, assume keywords are on single lines.
                    break
            if detected_section_type:
                break
        
        if detected_section_type:
            section_name = ""
            # Types that should be numbered if they appear multiple times
            numbered_types = {"verse", "chorus", "bridge"} 
            
            if detected_section_type in numbered_types:
                section_counter[detected_section_type] += 1
                section_name = f"{detected_section_type.capitalize()} {section_counter[detected_section_type]}"
            else: # For intro, outro, solo - use capitalized type name directly (no number)
                  # and don't increment their counters in section_counter for naming purposes.
                section_name = detected_section_type.capitalize()
                # If we wanted "Intro 1", "Solo 1", we'd use the counter like for verses.
                # The tests currently expect unnumbered for these.
                # section_counter[detected_section_type] += 1 # Only if we want to count occurrences

            section_start_time_est = i * time_per_line
            closest_chord_time = section_start_time_est
            if chords:
                for chord_entry in chords:
                    if chord_entry.get("time", 0.0) >= section_start_time_est:
                        closest_chord_time = chord_entry.get("time", section_start_time_est)
                        break
            
            structure.append({"type": section_name, "start_time": closest_chord_time})
            last_added_line_index = i # Mark this line as processed for section start

    if not structure and lines:  # Fallback if no structure found
        structure.append({"type": "Song", "start_time": 0.0})

    log.info(f"Identified {len(structure)} structural sections.")
    return {"structure": structure}
