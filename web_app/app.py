import os
import tempfile
import logging
import shutil
from typing import Dict, Any, List, Tuple, Optional

from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

from chord_extraction import get_chords, get_chords_batch, check_backend_availability
from key_transpose_capo.transpose import transpose_chords
from key_transpose_capo.capo_advisor import recommend_capo
from flourish_engine.rule_based import apply_rule_based_flourishes
from key_transpose_capo.key_analysis import detect_key_from_chords
from audio_input.utils import check_audio_file
from common.utils import format_error, serialize_result
from lyrics_analysis.lyrics_retriever import get_lyrics as get_lyrics_func
from lyrics_analysis.lyrics_analyzer import align_chords_with_lyrics, identify_song_structure

app = Flask(__name__)
log = logging.getLogger(__name__)

# Security: Limit upload size (e.g., 20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac'}

@app.route("/")
def index() -> Response:
    """Serves the main index.html file."""
    return send_from_directory(os.path.dirname(__file__), "index.html")

def process_chord_extraction(audio_input_source: Optional[str], is_url: bool) -> Tuple[Dict[str, Any], int]:
    """
    Helper function to handle chord extraction logic for both file uploads and URLs.
    Also attempts to retrieve lyrics and perform basic alignment/structure analysis.
    """
    temp_dir = None
    temp_filepath = None
    chords = []
    lyrics_text = ""
    
    try:
        if is_url:
            # get_chords now handles downloading from URL to a temp file internally
            chords = get_chords(audio_input_source)
            log.info(f"Successfully extracted chords from URL: {audio_input_source}")
            
            # Attempt to get lyrics for the URL
            lyrics_result = get_lyrics_func(url=audio_input_source)
            if "lyrics" in lyrics_result:
                lyrics_text = lyrics_result["lyrics"]
                log.info(f"Successfully retrieved lyrics for URL: {audio_input_source}")
            elif "error" in lyrics_result:
                log.warning(f"Could not retrieve lyrics for URL {audio_input_source}: {lyrics_result['error']}")
        else:
            # For file uploads, save to temp and then process
            audio = request.files['audio']
            filename = secure_filename(audio.filename)
            if not filename:
                log.warning("Invalid filename received")
                return jsonify(format_error("Invalid filename.")), 400

            temp_dir = tempfile.mkdtemp()
            temp_filepath = os.path.join(temp_dir, filename)
            audio.save(temp_filepath)
            check_audio_file(temp_filepath)
            chords = get_chords(temp_filepath)
            log.info(f"Successfully extracted chords from {filename}")
        
        aligned_lyrics = []
        song_structure = {"structure": []}

        if lyrics_text: # Only align and identify structure if lyrics were successfully retrieved
            aligned_lyrics = align_chords_with_lyrics(chords, lyrics_text)
            song_structure = identify_song_structure(lyrics_text, chords)

        return jsonify({
            "chords": chords,
            "lyrics": lyrics_text, # Return the actual lyrics text
            "aligned_lyrics": aligned_lyrics,
            "song_structure": song_structure
        }), 200
    except ValueError as e:
        log.error(f"File validation failed: {e}")
        return jsonify(format_error(f"Invalid file: {e}")), 400
    except Exception as e:
        log.error(f"Chord extraction failed for {audio_input_source}", exc_info=True)
        return jsonify(format_error("Chord extraction failed", e)), 500
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                log.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                log.error(f"Failed to clean up temporary directory {temp_dir}: {e}")

@app.route("/extract_chords", methods=["POST"])
def extract_chords_route() -> Tuple[Response, int]:
    """
    Handles single audio file upload and chord extraction.
    """
    log.info("Received request for /extract_chords (file upload)")
    if 'audio' not in request.files:
        log.warning("No audio file uploaded in /extract_chords request")
        return jsonify(format_error("No audio file uploaded.")), 400
    return process_chord_extraction(None, False) # Pass None for source, indicate it's a file upload

@app.route("/extract_chords_from_url", methods=["POST"])
def extract_chords_from_url_route() -> Tuple[Response, int]:
    """
    Handles chord extraction from a URL.
    """
    log.info("Received request for /extract_chords_from_url")
    data = request.get_json()
    url = data.get('url')
    if not url:
        log.warning("No URL provided for /extract_chords_from_url request")
        return jsonify(format_error("No URL provided.")), 400
    return process_chord_extraction(url, True) # Pass URL, indicate it's a URL

@app.route("/extract_chords_batch", methods=["POST"])
def extract_chords_batch_route() -> Tuple[Response, int]:
    """
    Accepts multiple audio files and returns extracted chords or errors for each.
    """
    log.info("Received request for /extract_chords_batch")
    if 'audios' not in request.files:
        log.warning("No audio files uploaded in /extract_chords_batch request")
        return jsonify(format_error("No audio files uploaded. Use 'audios' as the field name.")), 400

    files = request.files.getlist('audios')
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
            log.warning(f"Skipping file with invalid filename in batch: {audio.filename}")
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
                    log.error(f"Failed to unlink invalid temp file {temp_filepath}: {unlink_e}")

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
        result = {file_map[path]: batch_result.get(path, {"error": "Processing failed"}) for path in temp_paths}
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
    if not data or 'chords' not in data or 'semitones' not in data:
        log.warning("Missing data in /transpose request")
        return jsonify(format_error("Missing chords or semitones.")), 400

    try:
        chords = data['chords']
        semitones = int(data['semitones'])
        if not isinstance(chords, list) or not all(isinstance(c, dict) and 'chord' in c for c in chords):
            log.warning("Invalid chords format in /transpose request")
            return jsonify(format_error("Invalid chords format. Expected list of objects with 'chord' key.")), 400

        chord_strings = [c['chord'] for c in chords]
        transposed_strings = transpose_chords(chord_strings, semitones)

        transposed_chords = []
        for i, c in enumerate(chords):
            updated_chord = c.copy()
            updated_chord['chord'] = transposed_strings[i]
            transposed_chords.append(updated_chord)

        log.info("Transposition successful")
        return jsonify({"chords": transposed_chords}), 200
    except ValueError:
        log.warning("Invalid semitones value in /transpose request")
        return jsonify(format_error("Invalid semitones value. Must be an integer.")), 400
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
    if not data or 'chords' not in data:
        log.warning("Missing chords in /capo request")
        return jsonify(format_error("Missing chords.")), 400

    try:
        chords = data['chords']
        if not isinstance(chords, list) or not all(isinstance(c, dict) and 'chord' in c for c in chords):
            log.warning("Invalid chords format in /capo request")
            return jsonify(format_error("Invalid chords format. Expected list of objects with 'chord' key.")), 400

        chord_strings = [c['chord'] for c in chords]
        capo_fret, transposed_strings = recommend_capo(chord_strings)

        transposed_chords = []
        for i, c in enumerate(chords):
            updated_chord = c.copy()
            updated_chord['chord'] = transposed_strings[i]
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
    if not data or 'chords' not in data:
        log.warning("Missing chords in /flourish request")
        return jsonify(format_error("Missing chords.")), 400

    method = data.get("method", "rule_based")
    rule_set_name = data.get("rule_set_name", "default")

    try:
        chords = data['chords']
        if not isinstance(chords, list) or not all(isinstance(c, dict) and 'chord' in c for c in chords):
            log.warning("Invalid chords format in /flourish request")
            return jsonify(format_error("Invalid chords format. Expected list of objects with 'chord' key.")), 400

        chord_list = [c['chord'] for c in chords]
        flourishes = []

        if method == "magenta":
            from flourish_engine.magenta_flourish import generate_magenta_flourish
            flourishes = generate_magenta_flourish(chord_list)
            log.info("Magenta flourish generation requested")
        elif method == "gpt4all":
            from flourish_engine.gpt4all_flourish import suggest_chord_substitutions
            lyrics = data.get("lyrics")
            flourishes = suggest_chord_substitutions(chord_list, lyrics=lyrics)
            log.info("GPT4All flourish generation requested")
        elif method == "rule_based":
            flourishes = apply_rule_based_flourishes(chord_list, rule_set_name=rule_set_name)
            log.info(f"Rule-based flourish generation requested with rule set: {rule_set_name}")
        else:
            log.warning(f"Invalid flourish method requested: {method}")
            return jsonify(format_error(f"Invalid flourish method: {method}. Available methods: rule_based, magenta, gpt4all.")), 400

        return jsonify({"flourishes": flourishes}), 200
    except ValueError as e:
        log.warning(f"Invalid rule set name in /flourish request: {e}")
        return jsonify(format_error(f"Invalid rule set: {e}")), 400
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
    if not data or 'chords' not in data:
        log.warning("Missing chords in /key request")
        return jsonify(format_error("Missing chords.")), 400

    try:
        chords = data['chords']
        if not isinstance(chords, list) or not all(isinstance(c, dict) and 'chord' in c for c in chords):
            log.warning("Invalid chords format in /key request")
            return jsonify(format_error("Invalid chords format. Expected list of objects with 'chord' key.")), 400

        chord_strings = [c['chord'] for c in chords]
        key = detect_key_from_chords(chord_strings)
        log.info(f"Key detection successful: {key}")
        return jsonify({"key": key}), 200
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
        return jsonify(format_error("Audio download requires yt-dlp. Install with 'pip install yt-dlp'.")), 500
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

    lyrics_data = get_lyrics_func(url=url, title=title, artist=artist)

    if "error" in lyrics_data:
        log.error(f"Lyrics retrieval failed: {lyrics_data['error']}")
        return jsonify(format_error(lyrics_data['error'])), 500
    
    log.info("Lyrics retrieval successful")
    return jsonify({"lyrics": lyrics_data.get("lyrics", "")}), 200


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.run(debug=True)
