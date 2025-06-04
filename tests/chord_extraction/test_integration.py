"""
Integration and functional tests for Acoustic Cover Assistant CLI and web app.
Covers end-to-end flows for all major features.
"""
import os
import sys
import json
# import tempfile # Not used if CHORDS_SAMPLE_REL is used directly
import shutil # Keep shutil as it might be used by other tests or future ones
import pytest
from click.testing import CliRunner

# Add project root to sys.path for consistent imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cli.cli import cli as cli_main_group # Import the main Click group, aliased
from web_app.app import app as flask_app

AUDIO_SAMPLE_REL = os.path.join('tests', 'audio_input', 'guitar.wav')
CHORDS_SAMPLE_REL = os.path.join('tests', 'data', 'sample_chords.json')

AUDIO_SAMPLE_ABS = os.path.join(PROJECT_ROOT, AUDIO_SAMPLE_REL)
CHORDS_SAMPLE_ABS = os.path.join(PROJECT_ROOT, CHORDS_SAMPLE_REL)


@pytest.mark.skipif(not os.path.exists(AUDIO_SAMPLE_ABS), reason="No sample audio file present.")
def test_cli_extract_chords_full():
    runner = CliRunner()
    result = runner.invoke(cli_main_group, ['extract-chords', AUDIO_SAMPLE_REL])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert all('chord' in c and 'time' in c for c in data)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_cli_transpose_full():
    runner = CliRunner()
    result = runner.invoke(cli_main_group, ['transpose', CHORDS_SAMPLE_REL, '--semitones', '2'])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert all('chord' in c for c in data)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_cli_capo_full():
    runner = CliRunner()
    result = runner.invoke(cli_main_group, ['capo', CHORDS_SAMPLE_REL])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert 'capo' in data and 'chords' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_cli_flourish_full():
    runner = CliRunner()
    result = runner.invoke(cli_main_group, ['flourish', CHORDS_SAMPLE_REL])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert 'flourishes' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_cli_key_full():
    runner = CliRunner()
    result = runner.invoke(cli_main_group, ['key', CHORDS_SAMPLE_REL])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert 'key' in data

@pytest.mark.skipif(not os.path.exists(AUDIO_SAMPLE_ABS), reason="No sample audio file present.")
def test_web_extract_chords_full():
    client = flask_app.test_client()
    with open(AUDIO_SAMPLE_ABS, 'rb') as f:
        data_payload = {'audio': (f, os.path.basename(AUDIO_SAMPLE_REL))}
        response = client.post('/extract_chords', data=data_payload, content_type='multipart/form-data')
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert 'chords' in data
    assert isinstance(data['chords'], list)

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_web_transpose_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE_ABS) as f:
        chords_list = json.load(f)
    response = client.post('/transpose', json={'chords': chords_list, 'semitones': 2})
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert 'chords' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_web_capo_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE_ABS) as f:
        chords_list = json.load(f)
    response = client.post('/capo', json={'chords': chords_list})
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert 'capo' in data and 'chords' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_web_flourish_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE_ABS) as f:
        chords_list = json.load(f)
    response = client.post('/flourish', json={'chords': chords_list})
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert 'flourishes' in data

@pytest.mark.skipif(not os.path.exists(CHORDS_SAMPLE_ABS), reason="No sample chords JSON present.")
def test_web_key_full():
    client = flask_app.test_client()
    with open(CHORDS_SAMPLE_ABS) as f:
        chords_list = json.load(f)
    response = client.post('/key', json={'chords': chords_list})
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert 'key' in data

def test_web_backend_status_full():
    client = flask_app.test_client()
    response = client.get('/backend_status')
    assert response.status_code == 200, response.data
    data = response.get_json()
    assert isinstance(data, dict)
    assert 'autochord' in data
    assert 'chordino' in data
    assert 'chord_extractor' in data
