import pytest
import sys

def test_import_downloader():
    import audio_input.downloader

def test_download_audio_invalid_url(monkeypatch):
    from audio_input.downloader import download_audio
    # Patch yt_dlp.YoutubeDL to raise an exception
    class DummyYDL:
        def __init__(self, opts): pass
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def extract_info(self, url, download=True):
            raise Exception("Invalid URL")
        def prepare_filename(self, info): return "dummy.mp3"
    monkeypatch.setattr("yt_dlp.YoutubeDL", DummyYDL)
    with pytest.raises(Exception) as exc:
        download_audio("not_a_real_url")
    assert "Invalid URL" in str(exc.value)

def test_download_audio_missing_yt_dlp(monkeypatch):
    sys_modules_backup = dict(sys.modules)
    sys.modules["yt_dlp"] = None
    try:
        with pytest.raises(ImportError):
            import importlib
            importlib.reload(__import__("audio_input.downloader"))
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)
