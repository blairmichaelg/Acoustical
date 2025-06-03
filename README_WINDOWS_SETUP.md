# Windows Setup Instructions for Acoustical Project

## 1. Install Python Dependencies

Ensure you have Python 3.11 installed. Activate the virtual environment:
```pwsh
& c:\Users\Michael\acoustical\acp.venv\Scripts\Activate.ps1
```
Install required Python packages:
```pwsh
pip install -r requirements.txt
```

## 2. Download GPT4All Model

1. Visit [GPT4All](https://gpt4all.io/index.html).
2. Download a compatible model file, e.g., `ggml-gpt4all-j-v1.3-groovy.bin`.
3. Place the `.bin` file in the project root directory (`c:\Users\Michael\acoustical\`).

## 3. Run the Web App

Start the Flask web app:
```pwsh
python web_app\app.py
```
Access the app at `http://127.0.0.1:5000`.

## 4. Troubleshooting

- **Missing GPT4All Model:** Ensure the `.bin` file is in the correct location.
- **Dependency Issues:** Run `pip install gpt4all` manually if needed.
- **Magenta Errors:** Magenta is not supported on Windows. Use WSL/Linux for Magenta-based features.

## 5. Optional: Set Up WSL

For full functionality (Magenta, chord extraction), install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) and set up the project in a Linux environment.
