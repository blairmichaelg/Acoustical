import pytest
import sys
import os 
import importlib # For reloading
import builtins # Import the builtins module

# It's good practice to ensure audio_input is in path if tests are run from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_import_downloader():
    import audio_input.downloader # noqa: F401

def test_download_audio_invalid_url(monkeypatch):
    # This test assumes yt_dlp *is* importable, but its operations might fail.
    try:
        import yt_dlp # Try to import it to patch it
        class DummyYDL:
            def __init__(self, opts): pass
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): pass
            def extract_info(self, url, download=True):
                if url == "not_a_real_url":
                    raise Exception("Mocked YDL: Invalid URL")
                return {"title": "test_title", "ext": "mp3"} # Fallback for other calls
            def prepare_filename(self, info): return "dummy.mp3"
        
        # Patch the YoutubeDL class within the already imported yt_dlp module
        monkeypatch.setattr(yt_dlp, "YoutubeDL", DummyYDL)

    except ImportError:
        # If yt_dlp itself is not installed, this test is not meaningful in this form.
        # The test_download_audio_missing_yt_dlp covers the missing module scenario.
        pytest.skip("yt_dlp not installed, skipping test_download_audio_invalid_url which mocks its behavior.")

    from audio_input.downloader import download_audio
    with pytest.raises(Exception) as exc: # Expecting the downloader's generic Exception
        download_audio("not_a_real_url")
    # The downloader wraps yt_dlp's exception.
    assert "Audio download failed: Mocked YDL: Invalid URL" in str(exc.value)


def test_download_audio_missing_yt_dlp(monkeypatch):
    # Store original import function and sys.modules state
    original_import = builtins.__import__ # Use builtins module
    sys_modules_backup = sys.modules.copy()

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yt_dlp":
            raise ImportError("Simulated: yt_dlp module not found by __import__")
        return original_import(name, globals, locals, fromlist, level)

    # Patch the built-in import function
    monkeypatch.setattr(builtins, "__import__", mock_import) # Use builtins module

    # Ensure downloader module is re-evaluated if it was already imported
    if "audio_input.downloader" in sys.modules:
        importlib.reload(sys.modules["audio_input.downloader"])
        from audio_input.downloader import download_audio 
    else:
        from audio_input.downloader import download_audio 

    try:
        with pytest.raises(ImportError, match="yt-dlp is required. Install with 'pip install yt-dlp'."):
            download_audio("any_url_for_this_specific_test")
    finally:
        # monkeypatch automatically undoes the setattr on builtins after the test.
        # Restore sys.modules
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)
