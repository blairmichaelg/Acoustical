"""
Integration and functional tests for Acoustic Cover Assistant CLI and web app.
Covers end-to-end flows for all major features.
"""
import os
import sys
import json
import tempfile
import shutil
import pytest
from click.testing import CliRunner

# Add CLI and web_app to sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../cli')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../web_app')))
import cli
from web_app.app import app as flask_app

AUDIO_SAMPLE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../audio_input/guitar.wav'))
CHORDS_SAMPLE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/sample_chords.json'))

@pytest.mark.skipif(not os.path.exists(AUDIO_SAMPLE), reason="No sample audio file present.")
def test_cli_extract_chords_full():
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['extract-chords', AUDIO_SAMPLE])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert all('chord' in c and 'time' in c for c in data)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_cli_transpose_full():
    runner = CliRunner()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
        json.dump(chords, tmp)
        tmp.flush()
        result = runner.invoke(cli.cli, ['transpose', tmp.name, '--semitones', '2'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert all('chord' in c for c in data)
    os.unlink(tmp.name)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_cli_capo_full():
    runner = CliRunner()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
        json.dump(chords, tmp)
        tmp.flush()
        result = runner.invoke(cli.cli, ['capo', tmp.name])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'capo' in data and 'chords' in data
    os.unlink(tmp.name)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_cli_flourish_full():
    runner = CliRunner()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
        json.dump(chords, tmp)
        tmp.flush()
        result = runner.invoke(cli.cli, ['flourish', tmp.name])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'flourishes' in data
    os.unlink(tmp.name)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_cli_key_full():
    runner = CliRunner()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
        json.dump(chords, tmp)
        tmp.flush()
        result = runner.invoke(cli.cli, ['key', tmp.name])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'key' in data
    os.unlink(tmp.name)

@pytest.mark.skipif(not os.path.exists(AUDIO_SAMPLE), reason="No sample audio file present.")
def test_web_extract_chords_full():
    client = flask_app.test_client()
    with open(AUDIO_SAMPLE, 'rb') as f:
        data = {'audio': (f, 'guitar.wav')}
        response = client.post('/extract_chords', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'chords' in data
    assert isinstance(data['chords'], list)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_web_transpose_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    response = client.post('/transpose', json={'chords': chords, 'semitones': 2})
    assert response.status_code == 200
    data = response.get_json()
    assert 'chords' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_web_capo_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    response = client.post('/capo', json={'chords': chords})
    assert response.status_code == 200
    data = response.get_json()
    assert 'capo' in data and 'chords' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_web_flourish_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    response = client.post('/flourish', json={'chords': chords})
    assert response.status_code == 200
    data = response.get_json()
    assert 'flourishes' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_web_key_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE) as f:
        chords = json.load(f)
    response = client.post('/key', json={'chords': chords})
    assert response.status_code == 200
    data = response.get_json()
    assert 'key' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE), reason="No sample chords JSON present.")
def test_web_backend_status_full():
    client = flask_app.test_client()
    response = client.get('/backend_status')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert 'autochord' in data
    assert 'chordino' in data
    assert 'chord_extractor' in data
