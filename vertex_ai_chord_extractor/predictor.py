import os
import base64
import tempfile
import json
import logging
from urllib.parse import urlparse

from google.cloud import storage

from chord_extraction.essentia_wrapper import EssentiaBackend


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CustomPredictor:
    def __init__(self):
        """
        Initializes the predictor. This method is called once when the model
        server starts. It should load the model artifacts (if any) and prepare
        the backend.
        """
        self._backend = EssentiaBackend()
        self._storage_client = storage.Client()
        logger.info("EssentiaBackend and Google Cloud Storage client initialized for CustomPredictor.")

    def predict(self, instances):
        """
        Performs prediction using the EssentiaBackend.

        Args:
            instances: A list of input instances. Each instance is expected to
                       be a dictionary containing 'audio_b64' (base64 encoded
                       audio data) or 'audio_gcs_uri'.

        Returns:
            A list of predictions, where each prediction is the result from
            EssentiaBackend.
        """
        predictions = []
        for instance in instances:
            audio_path = None
            temp_file = None  # Initialize temp_file outside try block
            try:
                if 'audio_b64' in instance:
                    audio_data = base64.b64decode(instance['audio_b64'])
                    # Create a temporary file to store the audio data
                    # EssentiaBackend expects a file path
                    with tempfile.NamedTemporaryFile(delete=False,
                                                     suffix=".wav") as tmp:
                        tmp.write(audio_data)
                    audio_path = tmp.name
                    temp_file = tmp.name  # Store temp_file path for cleanup
                    logger.info(f"Processing audio from base64: {audio_path}")
                elif 'audio_gcs_uri' in instance:
                    gcs_uri = instance['audio_gcs_uri']
                    parsed_uri = urlparse(gcs_uri)
                    if parsed_uri.scheme != 'gs':
                        predictions.append({"error": "Invalid GCS URI scheme. Must start with 'gs://'."})
                        continue

                    bucket_name = parsed_uri.netloc
                    blob_name = parsed_uri.path.lstrip('/')

                    bucket = self._storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)

                    # Create a temporary file to download the GCS object to
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_name)[1]) as tmp:
                        blob.download_to_file(tmp)
                        audio_path = tmp.name
                        temp_file = tmp.name  # Store temp_file path for cleanup
                    logger.info(f"Downloaded {gcs_uri} to {audio_path}")
                else:
                    predictions.append({"error": "Missing 'audio_b64' or 'audio_gcs_uri' in instance."})
                    continue

                if audio_path:
                    # Call the EssentiaBackend's extract_chords method
                    chords = self._backend.extract_chords(audio_path)
                    predictions.append({"chords": chords})

            except Exception as e:
                logger.error(f"Prediction failed for instance: {e}",
                             exc_info=True)
                predictions.append({"error": str(e)})
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)  # Clean up temporary file

        return predictions


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Run Essentia Chord Extractor locally.")
    parser.add_argument("--audio_file_path", type=str, help="Path to the audio file for local testing.")
    args = parser.parse_args()

    predictor = CustomPredictor()

    test_instances = []
    if args.audio_file_path:
        # If a file path is provided, use it directly
        test_instances.append({"audio_gcs_uri": args.audio_file_path})
        logger.info(f"Using provided audio file for local test: {args.audio_file_path}")
    else:
        # Fallback to dummy audio if no file path is provided
        dummy_audio_content = (
            b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )
        dummy_audio_b64 = base64.b64encode(dummy_audio_content).decode('utf-8')
        test_instances.append({"audio_b64": dummy_audio_b64})
        logger.info("Using dummy audio for local test.")

    results = predictor.predict(test_instances)
    print(json.dumps(results, indent=2))
