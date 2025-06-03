"""
GPT4All LLM-based chord suggestion engine.
"""
import logging

try:
    from gpt4all import GPT4All
    _gpt4all_available = True
except ImportError:
    _gpt4all_available = False
    GPT4All = None


def suggest_chord_substitutions(chords, lyrics=None, model_path=None, max_tokens=64):
    """
    Suggest chord substitutions/extensions using GPT4All if available.
    Falls back to a static suggestion if GPT4All is not installed.
    Args:
        chords (list of str): List of chord symbols.
        lyrics (str, optional): Associated lyrics for context.
        model_path (str, optional): Path to GPT4All model file.
        max_tokens (int): Max tokens to generate per suggestion.
    Returns:
        list of str: Chord suggestions or substitutions.
    """
    if not _gpt4all_available:
        logging.warning("GPT4All is not installed. Returning static suggestions.")
        return [f"(No LLM) Try {c}maj7 or {c}9" for c in chords]

    if not model_path:
        model_path = "c:\\Users\\Michael\\acoustical\\ggml-gpt4all-j-v1.3-groovy.bin"
    try:
        model = GPT4All(model_path)
    except Exception as e:
        logging.error(f"Failed to load GPT4All model: {e}")
        return [f"(LLM unavailable) Try {c}7 or {c}add9" for c in chords]

    suggestions = []
    for chord in chords:
        prompt = f"Suggest a tasteful jazz or pop chord substitution or extension for the chord '{chord}'."
        if lyrics:
            prompt += f" The lyrics are: {lyrics}"
        try:
            response = model.generate(prompt, max_tokens=max_tokens)
            # Clean up and extract the suggestion
            suggestion = response.strip().split('\n')[0]
            suggestions.append(suggestion)
        except Exception as e:
            logging.error(f"GPT4All generation failed for '{chord}': {e}")
            suggestions.append(f"(LLM error) Try {chord}sus or {chord}6")
    return suggestions
