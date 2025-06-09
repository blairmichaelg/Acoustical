import logging

log = logging.getLogger(__name__)

def generate_magenta_flourish(chord_frames):
    """
    Generate 2–4 bar embellishments using Magenta improv_rnn.
    Currently a placeholder implementation.
    """
    log.warning("Magenta improv_rnn integration is not implemented. Returning static suggestions.")
    return [f"(Magenta unavailable) Consider embellishing {c} with arpeggios or passing tones." for c in chord_frames]
