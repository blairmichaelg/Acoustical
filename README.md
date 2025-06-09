# Acoustic Cover Assistant (Cloud-Enhanced)

![CI](https://github.com/blairmichaelg/Acoustical/actions/workflows/python-app.yml/badge.svg)
[![Cloud Build](https://storage.googleapis.com/cloud-build-badges/gen-lang-client-0894232365/trigger_id_placeholder.svg?branch=main)](https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0894232365)

A powerful, open-source tool designed for **beginner to intermediate singer/songwriters** to effortlessly analyze, adapt, and creatively transform songs. Acoustical, enhanced with **Google Cloud Platform (GCP)**, provides a scalable and intelligent pipeline to extract chords, retrieve lyrics, analyze key, transpose, recommend capo positions, and generate musical flourishes from any song.

Our vision is to empower you to **think of any song and instantly get the chords, lyrics, and creative progression ideas**, helping you put your own unique spin on covers or build new compositions, all powered by a robust cloud backend.

> **Note:** This project is now being enhanced with Google Cloud Platform for improved scalability, AI capabilities, and as a learning experience.

---

## Cloud Architecture Overview

Acoustical leverages several Google Cloud services to provide its features:

*   **Web Application Hosting:** The Flask web application is containerized and deployed on **Google Cloud Run**, providing a scalable, serverless environment.
*   **Audio & Data Storage:** **Google Cloud Storage (GCS)** is used for storing uploaded audio files, temporary processing files, and potentially cached analysis results.
*   **Chord Extraction:** The core Essentia-based chord extraction is deployed as a custom model on **Vertex AI Endpoints**, offering a scalable microservice.
*   **AI-Powered Creative Features:**
    *   **Magenta Flourishes:** Magenta models for musical flourish generation are intended to be deployed on **Vertex AI Endpoints**.
    *   **Chord Substitutions (LLM):** An LLM (like Google's Gemini via its API) is accessed through a **Google Cloud Function** to provide intelligent chord substitution suggestions.
*   **Lyrics Retrieval:** A **Google Cloud Function** may be used to orchestrate calls to external lyrics APIs or perform web scraping.
*   **CI/CD & Container Registry:** **Google Cloud Build** automates the building of Docker images, which are stored in **Google Artifact Registry**.
*   **API Key Management:** **Google Secret Manager** is used for securely storing any necessary API keys.

```mermaid
graph TD
    A[User: Web Browser] --> B[Cloud Run: Flask Web App];
    B --> C[GCS: Audio Uploads/Static Assets];
    B -- API Call --> D[Vertex AI Endpoint: Essentia Chord Extraction];
    D -- Reads Audio From --> C;
    B -- API Call --> E[Vertex AI Endpoint: Magenta Flourishes];
    B -- API Call --> F[Cloud Function: LLM Chord Subs (Gemini API)];
    B -- API Call --> G[Cloud Function: Lyrics Retrieval];
    
    H[Developer Push to Git] --> I[Cloud Build: CI/CD];
    I -- Builds & Pushes Image --> J[Artifact Registry];
    I -- Deploys --> B;
    I -- Deploys --> D;
    I -- Deploys --> E;
    I -- Deploys --> F;
    I -- Deploys --> G;

    subgraph "Google Cloud Platform"
        B
        C
        D
        E
        F
        G
        J
        direction LR
    end
```

---

## Quickstart & Deployment

This project is designed to be deployed on Google Cloud Platform.

**Prerequisites:**

1.  **Google Cloud SDK:** Install and initialize the `gcloud` CLI. ([Installation Guide](https://cloud.google.com/sdk/docs/install))
2.  **Google Cloud Project:** Have a GCP project created with billing enabled (though we aim for free tier usage where possible).
    *   Enable necessary APIs: Cloud Run, Vertex AI, Cloud Functions, Cloud Build, Artifact Registry, Cloud Storage, Secret Manager.
3.  **Docker:** Installed locally if you wish to build images locally before pushing.
4.  **Git:** For cloning the repository.

**Deployment Steps (High-Level):**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/blairmichaelg/Acoustical.git
    cd Acoustical
    ```
2.  **Configure GCP Project:**
    *   Set your GCP Project ID in `cloudbuild.yaml` and any other relevant configuration files (e.g., for service account permissions if needed).
    *   Store any required API keys (e.g., for external lyrics APIs, Gemini API key) in **Google Secret Manager**. Update the application to fetch secrets from there.
3.  **Build and Deploy Services using Cloud Build:**
    *   The primary method for deployment will be via `cloudbuild.yaml`. Trigger a build:
        ```bash
        gcloud builds submit --config cloudbuild.yaml .
        ```
    *   This will:
        *   Build Docker images for the web app (Cloud Run) and Vertex AI custom prediction routines (Essentia, Magenta).
        *   Push images to Artifact Registry.
        *   Deploy the web app to Cloud Run.
        *   Deploy models/predictors to Vertex AI Endpoints.
        *   Deploy Cloud Functions.
        *(Specific `cloudbuild.yaml` steps will need to be created for each service deployment beyond the initial Essentia container).*
4.  **Access the Web Application:**
    *   Once deployed, Cloud Run will provide a URL for the web application.

**(Local Development Note):** For local development, you might run the Flask app locally and configure it to point to deployed GCP services (Vertex AI, Cloud Functions). Alternatively, emulators for some services (like Firestore, Pub/Sub - though not heavily used yet) can be used. Direct local execution of all backends will become secondary to the cloud-deployed versions.

---

## Features

*   **Intelligent Chord Extraction (via Vertex AI):** Get chords from any audio file or direct URL, processed by a scalable Essentia backend on Vertex AI.
*   **Lyrics Retrieval (via Cloud Functions):** Fetch lyrics for songs, potentially orchestrated by Cloud Functions.
*   **Key Detection & Transposition:** Analyze song key and easily transpose chords.
*   **Capo Recommendation:** Get smart capo suggestions.
*   **Creative Flourish Generation (via Vertex AI & Cloud Functions):**
    *   **Magenta:** Generate musical embellishments using Magenta models hosted on Vertex AI.
    *   **LLM-Powered:** Get chord substitution ideas via Google's Gemini API, orchestrated by a Cloud Function.
    *   **Rule-Based:** (Can still run within the Cloud Run service or be a separate function).
*   **CLI & Web App Interfaces:** Interact with the tool via a user-friendly web interface (hosted on Cloud Run) or a CLI (which can be adapted to call the cloud APIs).

---
## Known Issues

*   Initial setup and configuration of GCP services require familiarity with Google Cloud.
*   Costs can be incurred if services scale beyond free tiers or if long-running instances are accidentally configured for Vertex AI endpoints (aim for scale-to-zero).
*   Network latency between services if not configured optimally (e.g., ensure services are in the same region).
*   Dependencies for specific models (Essentia, Magenta) are managed within their respective Docker containers for Vertex AI, simplifying the web app's direct dependencies.

---
## How to Add a New Backend/Plugin

While the original plugin system for local backends exists, for cloud-deployed features:

*   **New Chord Extraction Models:** Would typically involve creating a new custom prediction routine (Dockerfile, predictor.py) for Vertex AI, deploying it, and updating the web app to call the new endpoint.
*   **New Flourish Engines (AI-based):** Similar to above, deploy the model to Vertex AI or create a Cloud Function to interface with an external AI API.
*   **Rule-Based Logic:** Can still be added as Python modules within the Cloud Run service or deployed as separate Cloud Functions.

---
## Usage

### Web App (Primary Interface)

*   Access the application via the URL provided by Google Cloud Run after deployment.
*   Functionality remains similar: upload audio or paste a URL, extract chords, retrieve lyrics, transpose, capo, flourish, and download results. All backend processing is now handled by GCP services.

### CLI (Can be adapted)

*   The CLI (`cli/cli.py`) can be updated to make API calls to the deployed Cloud Run web app endpoints or directly to other GCP services (e.g., Vertex AI endpoints if secured appropriately). This ensures consistency between web and CLI usage.
    *   Example (conceptual):
        ```bash
        # Configure CLI to point to your Cloud Run URL
        acoustical config set api_endpoint <your-cloud-run-url>
        
        # Extract chords (CLI calls the cloud backend)
        acoustical extract-chords path/to/song.mp3 
        ```
---

## Audio Downloader

You can download audio from YouTube and other sites using the built-in downloader (requires `yt-dlp`):

**Install yt-dlp:**
```
pip install yt-dlp
```

**Python usage:**
```python
from audio_input.downloader import download_audio
download_audio("https://www.youtube.com/watch?v=...", out_dir="audio_input")
```

**Command-line usage:**
```
python audio_input/downloader.py <url> [--out_dir audio_input]
```

## Quickstart

1.  **Clone the repo and create a Python 3.11+ virtual environment.**
2.  **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```
    For advanced features (audio analysis, flourishes), uncomment optional lines in requirements.txt or use Poetry/Pipenv.
3.  **Run tests:**
    ```
    make test
    ```
4.  **Start the web app:**
    ```
    python web_app/app.py
    ```
    Open your browser at [http://localhost:5000](http://localhost:5000)

---

## API Usage

*   **Extract chords in Python (from file or URL):**
    ```python
    from chord_extraction import get_chords
    chords_from_file = get_chords("audio_input/song.mp3")
    chords_from_url = get_chords("https://www.youtube.com/watch?v=...")
    ```
*   **Batch extraction:**
    ```python
    from chord_extraction import get_chords_batch
    results = get_chords_batch(["file1.mp3", "file2.wav"])
    ```
*   **Retrieve lyrics:**
    ```python
    # Using the web app endpoint (example, actual implementation might vary)
    # This would typically be called from a frontend or another service
    import requests
    lyrics_data = requests.post("http://localhost:5000/get_lyrics", json={"url": "https://www.youtube.com/watch?v=..."}).json()
    print(lyrics_data.get("lyrics"))

    # Or directly via a Python function (future implementation)
    # from lyrics_retrieval import get_lyrics
    # lyrics = get_lyrics(url="https://www.youtube.com/watch?v=...")
    # lyrics = get_lyrics(title="Song Title", artist="Artist Name")
    ```
*   **Check backend availability:**
    ```python
    from chord_extraction import check_backend_availability
    print(check_backend_availability())
    ```

---

## Troubleshooting

*   If a backend fails, errors are logged and reported.
*   For missing dependencies, see requirements.txt and install only what you need.
*   Run `python check_backends.py` for backend diagnostics.
*   For more help, see [GitHub Issues](https://github.com/blairmichaelg/Acoustical/issues).

---

## Folder Structure

```
audio_input/                # Audio files or YouTube downloads
chord_extraction/           # Extraction modules and backend registry
key_transpose_capo/         # Key/capo logic
flourish_engine/            # Flourish/AI code
cli/                        # CLI interface
web_app/                    # Flask backend, minimal frontend
common/                     # Shared utilities (error formatting, serialization)
config.py                   # Centralized configuration
data/                       # Project files
tests/                      # Organized tests (e.g., chord_extraction/, flourish_engine/)
```

## Development & Contributing

*   Each module is documented with docstrings and sample I/O.
*   Add new extraction or flourish backends as plugins.
*   Run tests and linting with:
    ```
    make test
    make lint
    ```
*   Continuous Integration: All pushes and pull requests are tested and linted via [GitHub Actions](.github/workflows/python-app.yml).
*   See `/tests` and `/data` for examples.
*   Open a PR or issue for bugs, features, or questions.
*   Good first issues are labeled in [GitHub Issues](https://github.com/blairmichaelg/Acoustical/issues).

---

## Example JSON Output

```json
[
  {"time": 0.0, "chord": "G"},
  {"time": 2.5, "chord": "D"}
]
```

## AI Prompt Template (for AI/LLM Integration)

This template can be used to generate creative chord suggestions using an AI model:

```
Given this chord progression in key of G: [G, Em, C, D]
And these lyrics: “I walked along the riverside…”
Suggest three chord substitutions or extensions that fit mood.
```

---

## License

This project is licensed under the MIT license.
See the [LICENSE](LICENSE) file for details.

## Contact

Open issues or discussions on GitHub for support and ideas.
