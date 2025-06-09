# Windows Setup Instructions for Acoustical Project

## 1. Install Python Dependencies

Ensure you have Python 3.11 installed. Activate the virtual environment:
```pwsh
& c:\Users\Michael\acoustical\acp.venv\Scripts\Activate.ps1
```
Install core Python packages:
```pwsh
pip install -r requirements.txt
```
For optional, enhanced features (like advanced chord extraction or flourish generation), refer to `DEPENDENCY_INSTALLATION.md`.

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
- **Dependency Issues:** Refer to `DEPENDENCY_INSTALLATION.md` for detailed troubleshooting and installation instructions for optional dependencies.

## 5. Optional: Set Up WSL

For full functionality, especially for optional dependencies that are challenging to install on native Windows (e.g., Essentia, Magenta), consider installing [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) and setting up the project in a Linux environment within WSL.
