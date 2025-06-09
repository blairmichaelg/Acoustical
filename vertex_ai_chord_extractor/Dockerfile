FROM mtgupf/essentia-tensorflow:latest

# Install ffmpeg and its development libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswresample-dev \
    libavutil-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /essentia

# Copy the application code
COPY audio_input /essentia/audio_input
COPY chord_extraction /essentia/chord_extraction
COPY vertex_ai_chord_extractor/predictor.py /essentia/predictor.py
COPY vertex_ai_chord_extractor/requirements.txt /essentia/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /essentia/requirements.txt

# Set the entrypoint for Vertex AI prediction
ENTRYPOINT ["python3", "-m", "predictor"]
