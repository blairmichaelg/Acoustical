import logging
import os
import shutil
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import requests # For making HTTP requests to Vertex AI Endpoint
from google.cloud import storage
from flask import Flask, jsonify, request, send_from_directory, Response
from werkzeug.utils import secure_filename

from audio_input.utils import check_audio_file
from chord_extraction import check_backend_availability, \
    get_chords_batch # Removed get_chords
from common.utils import format_error, handle_exception
from flourish_engine.rule_based import apply_rule_based_flourishes
from key_transpose_capo.capo_advisor import recommend_capo
from key_transpose_capo.fingering_advisor import (
    suggest_fingerings as suggest_fingerings_lib,
)
from key_transpose_capo.key_analysis import detect_key_from_chords
from key_transpose_capo.transpose import transpose_chords
from lyrics_analysis.lyrics_analyzer import (
    align_chords_with_lyrics,
    identify_song_structure,
)
from lyrics_analysis.lyrics_retriever import get_lyrics_from_url_or_metadata
from music_theory.fretboard import Fretboard

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Configure logging at the module level
log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


app = Flask(__name__)

# Security: Limit upload size (e.g., 20MB)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac"}

# Initialize GCS client
storage_client = storage.Client()
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "acoustical-audio-uploads")

# Vertex AI Endpoint details for chord extraction
VERTEX_AI_PROJECT_ID = os.environ.get("VERTEX_AI_PROJECT_ID", "gen-lang-client-0894232365")
VERTEX_AI_REGION = os.environ.get("VERTEX_AI_REGION", "us-central1") # Default region
VERTEX_AI_ENDPOINT_ID = os.environ.get("VERTEX_AI_ENDPOINT_ID", "3741309315345022976") # Placeholder
VERTEX_AI_ENDPOINT_URL = (
    f"https://{VERTEX_AI_REGION}-aiplatform.googleapis.com/v1/projects/"
    f"{VERTEX_AI_PROJECT_ID}/locations/{VERTEX_AI_REGION}/endpoints/"
    f"{VERTEX_AI_ENDPOINT_ID}:predict"
)
log.info(f"Vertex AI Endpoint URL: {VERTEX_AI_ENDPOINT_URL}")


@app.route("/")
def index() -> Response:
    """Serves the main index.html file."""
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.errorhandler(Exception)
def handle_all_exceptions(e):
    """Global exception handler to return JSON errors."""
    log.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify(handle_exception(e, "Server error")), 500


def process_chord_extraction(
    audio_input_source: Optional[str], is_url: bool
) -> Tuple[Dict[str, Any], int]:
    """
    Helper function to handle chord extraction logic for both file uploads and URLs.
    Also attempts to retrieve lyrics and perform basic alignment/structure analysis.
    """
    gcs_uri = None
    lyrics_text = ""

    try:
        # Determine the GCS URI for the audio input
        if is_url:
            # If the input is a URL, assume it's already a GCS URI or a publicly accessible URL
            # that can be passed to the Vertex AI endpoint.
            # For now, we'll assume it's a GCS URI for the Vertex AI call.
            # In a real scenario, if it's a public URL, you might download it to GCS first.
            gcs_uri = audio_input_source
            log.info(f"Processing audio from URL (assumed GCS URI): {gcs_uri}")

            # Attempt to get lyrics for the URL
            lyrics_info = get_lyrics_from_url_or_metadata(url=audio_input_source)
            if lyrics_info.get("lyrics_text"):  # If lyrics were directly retrieved
                lyrics_text = lyrics_info["lyrics_text"]
                log.info(f"Successfully retrieved lyrics for URL: {audio_input_source}")
            elif lyrics_info.get("method") == "placeholder_url":
                lyrics_text = (
                    f"Lyrics for song from URL: {lyrics_info['url']}\n\n"
                    "(Placeholder lyrics: Verse 1...\nChorus...\nVerse 2...)"
                )
                log.info(
                    "Successfully retrieved placeholder lyrics for URL: "
                    f"{audio_input_source}"
                )
            elif "error" in lyrics_info:
                log.warning(
                    f"Could not retrieve lyrics for URL {audio_input_source}: "
                    f"{lyrics_info['error']}"
                )
        else:
            # For file uploads, upload to GCS
            audio = request.files["audio"]
            filename = secure_filename(audio.filename)
            if not filename:
                log.warning("Invalid filename received")
                return jsonify(format_error("Invalid filename.")), 400

            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.upload_from_file(audio, rewind=True)
            gcs_uri = f"gs://{GCS_BUCKET_NAME}/{filename}"
            log.info(f"Successfully uploaded {filename} to GCS: {gcs_uri}")

        # Call Vertex AI Endpoint for chord extraction
        headers = {"Authorization": f"Bearer {os.environ.get('GCP_ACCESS_TOKEN')}"} # Requires authentication
        data = {"instances": [{"audio_gcs_uri": gcs_uri}]}
        
        log.info(f"Sending request to Vertex AI Endpoint: {VERTEX_AI_ENDPOINT_URL}")
        response = requests.post(VERTEX_AI_ENDPOINT_URL, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for HTTP errors

        vertex_ai_response = response.json()
        predictions = vertex_ai_response.get("predictions", [])
        
        if predictions and "chords" in predictions[0]:
            chords = predictions[0]["chords"]
            log.info(f"Successfully extracted chords from Vertex AI for {gcs_uri}")
        else:
            log.error(f"Unexpected response from Vertex AI: {vertex_ai_response}")
            return jsonify(format_error("Failed to get chords from Vertex AI.")), 500

        aligned_lyrics = []
        song_structure = {"structure": []}

        if lyrics_text:  # Only align and identify structure if lyrics were retrieved
            aligned_lyrics = align_chords_with_lyrics(chords, lyrics_text)
            song_structure = identify_song_structure(lyrics_text, chords)

        return (
            jsonify(
                {
                    "chords": chords,
                    "lyrics": lyrics_text,  # Return the actual lyrics text
                    "aligned_lyrics": aligned_lyrics,
                    "song_structure": song_structure,
                }
            ),
            200,
        )
    except ValueError as e:
        log.error(f"File validation failed: {e}")
        return jsonify(format_error(f"Invalid file: {e}")), 400
    except Exception as e:
        log.error(
            f"Chord extraction failed for {audio_input_source or gcs_uri}",
            exc_info=True
        )
        return jsonify(format_error("Chord extraction failed", e)), 500


@app.route("/extract_chords", methods=["POST"])
def extract_chords_route() -> Tuple[Response, int]:
    """
    Handles single audio file upload and chord extraction.
    """
    log.info("Received request for /extract_chords (file upload)")
    if "audio" not in request.files:
        log.warning("No audio file uploaded in /extract_chords request")
        return jsonify(format_error("No audio file uploaded.")), 400
    return process_chord_extraction(None, False)


@app.route("/extract_chords_from_url", methods=["POST"])
def extract_chords_from_url_route() -> Tuple[Response, int]:
    """
    Handles chord extraction from a URL.
    """
    log.info("Received request for /extract_chords_from_url")
    data = request.get_json()
    url = data.get("url")
    if not url:
        log.warning("No URL provided for /extract_chords_from_url request")
        return jsonify(format_error("Missing URL.")), 400
    return process_chord_extraction(url, True)


@app.route("/extract_chords_batch", methods=["POST"])
def extract_chords_batch_route() -> Tuple[Response, int]:
    """
    Accepts multiple audio files and returns extracted chords or errors for each.
    """
    log.info("Received request for /extract_chords_batch")
    if "audios" not in request.files:
        log.warning("No audio files uploaded in /extract_chords_batch request")
        return (
            jsonify(format_error(
                "No audio files uploaded. Use 'audios' as the field name."
            )),
            400,
        )

    files = request.files.getlist("audios")
    if not files:
        log.warning("No audio files found in /extract_chords_batch request")
        return jsonify(format_error("No audio files found in request.")), 400

    temp_dir = tempfile.mkdtemp()
    temp_paths = []
    file_map = {}
    valid_files_count = 0

    for audio in files:
        filename = secure_filename(audio.filename)
        if not filename:
            log.warning(
                f"Skipping file with invalid filename in batch: {audio.filename}"
            )
            continue
        temp_filepath = os.path.join(temp_dir, filename)
        try:
            audio.save(temp_filepath)
            check_audio_file(temp_filepath)
            temp_paths.append(temp_filepath)
            file_map[temp_filepath] = filename
            valid_files_count += 1
        except Exception as e:
            log.warning(f"Skipping invalid file {filename} in batch: {e}")
            if os.path.exists(temp_filepath):
                try:
                    os.unlink(temp_filepath)
                except Exception as unlink_e:
                    log.error(
                        f"Failed to unlink invalid temp file {temp_filepath}: {unlink_e}"
                    )

    if not temp_paths:
        log.warning("No valid audio files uploaded in batch after validation")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                log.error(f"Failed to clean up temporary directory {temp_dir}: {e}")
        return jsonify(format_error("No valid audio files uploaded.")), 400

    log.info(f"Processing {valid_files_count} valid files in batch")
    try:
        batch_result = get_chords_batch(temp_paths)
        # Map temp file paths back to original filenames
        result = {
            file_map[path]: batch_result.get(path, {"error": "Processing failed"})
            for path in temp_paths
        }
        log.info("Batch chord extraction complete")
        return jsonify(result), 200
    except Exception as e:
        log.error("Batch chord extraction failed", exc_info=True)
        return jsonify(format_error("Batch chord extraction failed", e)), 500
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                log.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                log.error(f"Failed to clean up temporary directory {temp_dir}: {e}")


@app.route("/transpose", methods=["POST"])
def transpose_route() -> Tuple[Response, int]:
    """
    Handles transposition request.
    """
    log.info("Received request for /transpose")
    data = request.get_json()
    if not data or "chords" not in data or "semitones" not in data:
        log.warning("Missing data in /transpose request")
        return jsonify(format_error("Missing chords or semitones.")), 400

    try:
        chords = data["chords"]
        semitones_val = int(data["semitones"])
        if not isinstance(chords, list) or not all(
            isinstance(c, dict) and "chord" in c for c in chords
        ):
            log.warning("Invalid chords format in /transpose request")
            return (
                jsonify(format_error(
                    "Invalid chords format. Expected list of objects with 'chord' key."
                )),
                400,
            )

        chord_strings = [c["chord"] for c in chords]
        transposed_strings = transpose_chords(chord_strings, semitones_val)

        transposed_chords = []
        for i, c in enumerate(chords):
            updated_chord = c.copy()
            updated_chord["chord"] = transposed_strings[i]
            transposed_chords.append(updated_chord)

        log.info("Transposition successful")
        return jsonify({"chords": transposed_chords}), 200
    except ValueError:
        log.warning("Invalid semitones value in /transpose request")
        return (
            jsonify(format_error(
                "Invalid semitones value. Must be an integer."
            )),
            400,
        )
    except Exception as e:
        log.error("Transposition failed", exc_info=True)
        return jsonify(format_error("Transposition failed", e)), 500


@app.route("/capo", methods=["POST"])
def capo_route() -> Tuple[Response, int]:
    """
    Handles capo recommendation request.
    """
    log.info("Received request for /capo")
    data = request.get_json()
    if not data or "chords" not in data:
        log.warning("Missing chords in /capo request")
        return jsonify(format_error("Missing chords.")), 400

    try:
        chords = data["chords"]
        if not isinstance(chords, list) or not all(
            isinstance(c, dict) and "chord" in c for c in chords
        ):
            log.warning("Invalid chords format in /capo request")
            return (
                jsonify(format_error(
                    "Invalid chords format. Expected list of objects with 'chord' key."
                )),
                400,
            )

        chord_strings = [c["chord"] for c in chords]
        capo_fret, transposed_strings = recommend_capo(chord_strings)

        transposed_chords = []
        for i, c in enumerate(chords):
            updated_chord = c.copy()
            updated_chord["chord"] = transposed_strings[i]
            transposed_chords.append(updated_chord)

        log.info(f"Capo recommendation successful: Fret {capo_fret}")
        return jsonify({"capo": capo_fret, "chords": transposed_chords}), 200
    except Exception as e:
        log.error("Capo recommendation failed", exc_info=True)
        return jsonify(format_error("Capo recommendation failed", e)), 500


@app.route("/flourish", methods=["POST"])
def flourish_route() -> Tuple[Response, int]:
    """
    Handles flourish generation request.
    """
    log.info("Received request for /flourish")
    data = request.get_json()
    if not data or "chords" not in data:  # Expects list of chord objects
        log.warning("Missing chords in /flourish request")
        return jsonify(format_error("Missing chords (expected list of objects).")), 400

    method = data.get("method", "rule_based")  # rule_based, gpt4all, magenta
    rule_set_name = data.get("rule_set_name", "default")  # For rule_based
    lyrics_context = data.get("lyrics")  # For gpt4all

    try:
        chord_progression_objects = data[
            "chords"
        ]  # List of {"chord": "Am", "time": 0.0}
        if not isinstance(chord_progression_objects, list) or not all(
            isinstance(c, dict) and "chord" in c for c in chord_progression_objects
        ):
            log.warning("Invalid chords format in /flourish request")
            return (
                jsonify(format_error(
                    "Invalid chords format. Expected list of objects with 'chord' key."
                )),
                400,
            )

        flourishes_result = []

        if method == "magenta":
            from flourish_engine.magenta_flourish import generate_magenta_flourish

            # Magenta might need just strings, or adapt it to take objects
            chord_strings_for_magenta = [c["chord"] for c in chord_progression_objects]
            flourishes_result = generate_magenta_flourish(chord_strings_for_magenta)
            log.info("Magenta flourish generation requested")
        elif method == "gpt4all":
            from flourish_engine.gpt4all_flourish import (
                suggest_chord_substitutions as gpt4all_suggest,
            )

            flourishes_result = gpt4all_suggest(
                chord_progression_objects, lyrics=lyrics_context
            )
            log.info("GPT4All flourish generation requested")
        elif method == "rule_based":
            flourishes_result = apply_rule_based_flourishes(
                chord_progression_objects, rule_set_name=rule_set_name
            )
            log.info(
                f"Rule-based flourish generation requested with rule set: {rule_set_name}"
            )
        else:
            log.warning(f"Invalid flourish method requested: {method}")
            return (
                jsonify(format_error(
                    f"Invalid flourish method: {method}. Available methods: "
                    "rule_based, gpt4all, magenta."
                )),
                400,
            )
        # Ensure consistent output format if different engines return differently
        return jsonify({"flourishes": flourishes_result}), 200
    except ValueError as e:  # For invalid rule_set_name from rule_based
        log.warning(f"Invalid input for /flourish: {e}")
        return jsonify(format_error(f"Invalid input: {e}")), 400
    except Exception as e:
        log.error("Flourish suggestion failed", exc_info=True)
        return jsonify(format_error("Flourish suggestion failed", e)), 500


@app.route("/key", methods=["POST"])
def key_route() -> Tuple[Response, int]:
    """
    Handles key detection request.
    """
    log.info("Received request for /key")
    data = request.get_json()
    if not data or "chords" not in data:
        log.warning("Missing chords in /key request")
        return jsonify(format_error("Missing chords.")), 400

    try:
        chords = data["chords"]
        if not isinstance(chords, list) or not all(
            isinstance(c, dict) and "chord" in c for c in chords
        ):
            log.warning("Invalid chords format in /key request")
            return (
                jsonify(format_error(
                    "Invalid chords format. Expected list of objects with 'chord' key."
                )),
                400,
            )

        chord_strings = [c["chord"] for c in chords]
        key_info = detect_key_from_chords(chord_strings)  # Returns a dict
        log.info(f"Key detection successful: {key_info}")
        return jsonify(key_info), 200  # Return the whole dict
    except Exception as e:
        log.error("Key detection failed", exc_info=True)
        return jsonify(format_error("Key detection failed", e)), 500


@app.route("/backend_status", methods=["GET"])
def backend_status() -> Tuple[Response, int]:
    """
    Returns the availability status of chord extraction backends.
    """
    log.info("Received request for /backend_status")
    try:
        availability = check_backend_availability()
        log.info("Backend status check successful")
        return jsonify(availability), 200
    except Exception as e:
        log.error("Backend status check failed", exc_info=True)
        return jsonify(format_error("Backend status check failed", e)), 500


@app.route("/download_audio", methods=["POST"])
def download_audio_route() -> Tuple[Response, int]:
    """
    Handles audio download request from a URL.
    """
    log.info("Received request for /download_audio")
    data = request.get_json()
    if not data or "url" not in data:
        log.warning("Missing URL in /download_audio request")
        return jsonify(format_error("Missing URL.")), 400

    url = data["url"]
    out_dir = data.get("out_dir", "audio_input")

    try:
        from audio_input.downloader import download_audio

        path = download_audio(url, out_dir)
        filename = os.path.basename(path)
        log.info(f"Audio download successful: {filename}")
        return jsonify({"success": True, "filename": filename, "path": path}), 200
    except ImportError:
        log.error("yt-dlp not installed for audio download")
        return (
            jsonify(format_error(
                "Audio download requires yt-dlp. Install with 'pip install yt-dlp'."
            )),
            500,
        )
    except Exception as e:
        log.error(f"Audio download failed for URL {url}", exc_info=True)
        return jsonify(format_error("Audio download failed", e)), 500


@app.route("/get_lyrics", methods=["POST"])
def get_lyrics_route() -> Tuple[Response, int]:
    """
    Handles lyrics retrieval request.
    Accepts either 'url' or 'title' and 'artist'.
    """
    log.info("Received request for /get_lyrics")
    data = request.get_json()

    url = data.get("url")
    title = data.get("title")
    artist = data.get("artist")

    if not (url or (title and artist)):
        log.warning("Missing URL or title/artist in /get_lyrics request")
        return jsonify(format_error("Missing URL or song title/artist.")), 400

    lyrics_info = get_lyrics_from_url_or_metadata(url=url, title=title, artist=artist)

    # Simplified logic: get_lyrics_from_url_or_metadata should handle fetching or return placeholders
    # No direct MCP tool interaction from CLI for now.
    if lyrics_info["lyrics_text"]:  # If lyrics were directly retrieved
        return (
            jsonify(
                {"lyrics": lyrics_info["lyrics_text"], "source": lyrics_info["method"]}
            ),
            200,
        )
    elif lyrics_info["method"] == "scrape_azlyrics":
        # If it's azlyrics, but lyrics_text is empty, it means fetching/parsing failed internally
        return (
            jsonify(format_error(
                "Failed to retrieve lyrics from AZLyrics.",
                "Could not parse lyrics from the page or fetching failed.",
            )),
            500,
        )
    elif lyrics_info["method"] == "placeholder_url":
        lyrics_text = (
            f"Lyrics for song from URL: {lyrics_info['url']}\n\n"
            "(Placeholder lyrics: Verse 1...\nChorus...\nVerse 2...)"
        )
        return jsonify({"lyrics": lyrics_text, "source": "placeholder_url"}), 200
    else:
        return (
            jsonify(format_error(
                "Unknown lyrics retrieval method or no lyrics found.",
                f"Method: {lyrics_info['method']}",
            )),
            500,
        )


@app.route("/suggest_fingerings", methods=["POST"])
def suggest_fingerings_route() -> Tuple[Response, int]:
    """
    Suggests guitar fingerings for a given chord string.
    """
    log.info("Received request for /suggest_fingerings")
    data = request.get_json()
    if not data or "chord_string" not in data:
        log.warning("Missing chord_string in /suggest_fingerings request")
        return jsonify(format_error("Missing chord_string.")), 400

    chord_str = data["chord_string"]
    num_suggestions = data.get("num_suggestions", 5)
    tuning_str = data.get("tuning")  # e.g., "E,A,D,G,B,e"

    try:
        fretboard_tuning: Optional[List[str]] = None
        if tuning_str:
            fretboard_tuning = [s.strip() for s in tuning_str.split(",")]

        fb = Fretboard(tuning=fretboard_tuning)
        suggestions_with_scores = suggest_fingerings_lib(chord_str, fretboard=fb)

        if not suggestions_with_scores:
            return jsonify({"chord": chord_str, "suggestions": []}), 200

        output_suggestions = []
        for i, (shape, score) in enumerate(
            suggestions_with_scores
        ):  # Use score directly
            if i >= num_suggestions:
                break
            output_suggestions.append(
                {
                    "name": shape.name,
                    "root": shape.template_root_note_str,  # Actual root
                    "type": shape.chord_type,
                    "base_fret": shape.base_fret_of_template,  # Actual barre fret
                    "fingerings": shape.fingerings,
                    "score": score,
                    "is_movable": shape.is_movable,
                    "barre_strings": shape.barre_strings_offset,
                }
            )

        return jsonify({"chord": chord_str, "suggestions": output_suggestions}), 200

    except Exception as e:
        log.error(
            f"Error in suggest_fingerings route for '{chord_str}': {e}", exc_info=True
        )
        return (
            jsonify(format_error(
                f"Failed to suggest fingerings for '{chord_str}'.", e
            )),
            500,
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    app.run(debug=True)
