# Acoustical Project: Dependency Installation Guide

This guide provides detailed instructions for installing dependencies for the Acoustical project.

**General Recommendations:**

*   **Use a Virtual Environment:** Always install Python packages in a virtual environment to avoid conflicts with system-wide packages.
    ```bash
    python -m venv acp_env
    # Windows
    acp_env\Scripts\activate
    # macOS/Linux
    source acp_env/bin/activate
    ```
*   **Pip:** Ensure you have the latest version of pip:
    ```bash
    python -m pip install --upgrade pip
    ```
*   **Check `requirements.txt`:** Refer to the `requirements.txt` file for specific versions.

---

## Core Dependencies (Required for basic functionality):

Install these first:
```bash
pip install -r requirements.txt
```

---

## Optional Dependencies (For enhanced functionality):

Some features of Acoustical rely on external libraries that can be challenging to install, especially on Windows, due to their reliance on C++ compilers and specific system configurations. These dependencies are **optional**, and the application is designed to function without them, albeit with reduced capabilities in certain areas (e.g., chord extraction quality).

### 1. Chord Extraction Backends

Acoustical attempts to use available chord extraction backends in a fallback order. For the most accessible experience on Windows, `autochord` is recommended, followed by the `chord-extractor` CLI. `Essentia` offers the highest quality but is the most difficult to install on Windows.

*   **Autochord (Recommended for Windows accessibility):**
    A Python library for chord extraction.
    ```bash
    pip install autochord
    ```
    *Note: `autochord` may have its own complex dependencies (like `vamp`, `numba`, `llvmlite`) that can be difficult to build on Windows. If `pip install autochord` fails, consider searching for pre-built `.whl` files for `vamp` and `numba` (e.g., on Christoph Gohlke's website) and installing them manually before retrying `autochord`.*

*   **Chord-Extractor CLI (Alternative accessible option):**
    A command-line tool that can be wrapped by Acoustical.
    *   **Installation:** This is a standalone executable. You will need to download the appropriate binary for your system from its official GitHub releases page (search for "chord-extractor github"). Place the executable in a directory included in your system's PATH.
    *   *Note: This tool often relies on other external libraries like `FFmpeg` or `libsndfile` which might need separate installation.*

*   **Essentia (Advanced, Highest Quality, Linux/macOS Recommended):**
    A powerful C++ library with Python bindings for advanced audio analysis.
    *   **Windows:** Direct installation of Python bindings on native Windows is **not officially supported** and is highly complex. It is strongly recommended to use [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) and install Essentia within a WSL environment, or use a Linux/macOS system.
    *   **Linux/macOS:**
        ```bash
        pip install essentia
        ```
        If `pip` fails, refer to the official Essentia [installation guide](https://essentia.upf.edu/documentation/installing.html) for system-level dependencies or building from source.

### 2. Magenta (For advanced flourish generation)

Magenta is a Google Brain project for generating music and art using machine learning.
```bash
pip install magenta
```
*Note: Magenta has many dependencies, including TensorFlow, which can be challenging to install on Windows. Ensure your Python version is compatible. Best experience on Linux/macOS.*

### 3. Aubio (For enhanced audio analysis)

Aubio is a tool for audio labeling and music analysis.
```bash
pip install aubio
```
*Note: `aubio` generally installs well via `pip` on most platforms, but if issues arise on Windows, consider searching for pre-built `.whl` files.*

---

## Troubleshooting Tips:

*   **Compiler Errors:** If you see errors related to C/C++ compilation, you're missing a compiler (e.g., GCC on Linux, Clang on macOS, Visual Studio Build Tools on Windows) or development headers for a library. For Windows, installing "Desktop development with C++" via the Visual Studio Installer is often required for many Python packages with C/C++ extensions.
*   **Python Version:** Some libraries might have specific Python version compatibilities. Acoustical targets Python 3.11+, but check individual library requirements if issues persist.
*   **Operating System:** Some libraries have better support or easier installation on Linux/macOS than on Windows.
*   **Check GitHub Issues:** Look at the official GitHub repositories for these libraries for specific installation troubleshooting threads.

---

If you continue to experience issues, please open an issue on the [Acoustical GitHub repository](https://github.com/blairmichaelg/Acoustical/issues) with details about your operating system, Python version, and the full error message.
