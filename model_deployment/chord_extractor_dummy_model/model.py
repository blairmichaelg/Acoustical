import json
import numpy as np

class ChordExtractorModel:
    def __init__(self):
        """
        Initializes the dummy Chord Extractor Model.
        In a real scenario, this would load a pre-trained model.
        """
        print("Dummy Chord Extractor Model initialized.")

    def predict(self, instances):
        """
        Simulates chord extraction prediction.
        Args:
            instances: A list of input instances (e.g., audio features).
                       Each instance is expected to be a dictionary.
        Returns:
            A list of dictionaries, each containing a 'chords' key with dummy chord data.
        """
        predictions = []
        for instance in instances:
            # In a real model, 'instance' would be processed to extract features
            # and then fed into the loaded model to predict chords.
            # For this dummy, we'll just return a fixed set of chords or
            # a simple response based on input.
            if "audio_features" in instance:
                # Simulate a simple response based on input presence
                chords = ["Cmaj", "Gmaj", "Am", "Fmaj"]
                if len(instance["audio_features"]) > 5:
                    chords.append("D7")
                predictions.append({"chords": chords, "message": "Dummy prediction based on audio features."})
            else:
                predictions.append({"chords": ["N.C."], "message": "No audio features provided, returning No Chord."})
        return predictions

if __name__ == '__main__':
    # Example usage for local testing
    model = ChordExtractorModel()
    test_instances = [
        {"audio_features": [0.1, 0.2, 0.3, 0.4, 0.5]},
        {"audio_features": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]},
        {"some_other_data": "test"}
    ]
    results = model.predict(test_instances)
    print(json.dumps(results, indent=2))
