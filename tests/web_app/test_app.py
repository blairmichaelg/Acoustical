import unittest
import logging
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from flask import jsonify
from werkzeug.datastructures import FileStorage

# Adjust path to import app correctly
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from web_app.app import app, process_chord_extraction
from music_theory.chord_shapes import ChordShape

class TestWebApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('flask').setLevel(logging.WARNING)

    def tearDown(self):
        pass

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<!DOCTYPE html>", response.data)

    @patch('web_app.app.get_chords')
    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    @patch('web_app.app.align_chords_with_lyrics')
    @patch('web_app.app.identify_song_structure')
    @patch('web_app.app.check_audio_file')
    @patch('web_app.app.tempfile.mkdtemp', return_value='mock_temp_dir')
    @patch('web_app.app.shutil.rmtree')
    @patch('builtins.open', new_callable=MagicMock) # Mock open for FileStorage.save
    def test_process_chord_extraction_file_success(self, mock_open, mock_rmtree, mock_mkdtemp, mock_check_audio_file, mock_identify_song_structure, mock_align_chords_with_lyrics, mock_get_lyrics_from_url_or_metadata, mock_get_chords):
        mock_get_chords.return_value = [{"chord": "C", "time": 0.0}]
        mock_get_lyrics_from_url_or_metadata.return_value = {"lyrics_text": "Mock lyrics", "method": "metadata"}
        mock_align_chords_with_lyrics.return_value = ["Aligned C"]
        mock_identify_song_structure.return_value = {"structure": ["Verse"]}

        mock_audio_file = FileStorage(
            stream=MagicMock(), # Use MagicMock for stream
            filename='test_audio.mp3',
            content_type='audio/mpeg'
        )
        with app.app_context():
            with app.test_request_context():
                with patch('web_app.app.request') as mock_request:
                    mock_request.files = {'audio': mock_audio_file}
                    mock_request.files.getlist.return_value = [mock_audio_file]
                    mock_request.files['audio'].filename = 'test_audio.mp3'

                    response_data, status_code = process_chord_extraction(None, False)
                    
                    self.assertEqual(status_code, 200)
                    self.assertEqual(response_data.json['chords'], [{"chord": "C", "time": 0.0}])
                    self.assertEqual(response_data.json['lyrics'], "Mock lyrics")
                    self.assertEqual(response_data.json['aligned_lyrics'], ["Aligned C"])
                    self.assertEqual(response_data.json['song_structure'], {"structure": ["Verse"]})
                    
                    mock_get_chords.assert_called_once_with(os.path.join('mock_temp_dir', 'test_audio.mp3'))
                    mock_check_audio_file.assert_called_once_with(os.path.join('mock_temp_dir', 'test_audio.mp3'))
                    mock_rmtree.assert_called_once_with('mock_temp_dir')
                    mock_open.assert_called_once_with(os.path.join('mock_temp_dir', 'test_audio.mp3'), 'wb')

    @patch('web_app.app.get_chords')
    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    @patch('web_app.app.align_chords_with_lyrics')
    @patch('web_app.app.identify_song_structure')
    @patch('web_app.app.check_audio_file')
    @patch('web_app.app.tempfile.mkdtemp', return_value='mock_temp_dir')
    @patch('web_app.app.shutil.rmtree')
    def test_process_chord_extraction_url_success(self, mock_rmtree, mock_mkdtemp, mock_check_audio_file, mock_identify_song_structure, mock_align_chords_with_lyrics, mock_get_lyrics_from_url_or_metadata, mock_get_chords):
        mock_get_chords.return_value = [{"chord": "G", "time": 0.0}]
        mock_get_lyrics_from_url_or_metadata.return_value = {"lyrics_text": "URL lyrics", "method": "url_scrape", "url": "http://example.com/song.mp3"}
        mock_align_chords_with_lyrics.return_value = ["Aligned G"]
        mock_identify_song_structure.return_value = {"structure": ["Chorus"]}

        url = "http://example.com/song.mp3"
        with app.app_context():
            response_data, status_code = process_chord_extraction(url, True)
            
            self.assertEqual(status_code, 200)
            self.assertEqual(response_data.json['chords'], [{"chord": "G", "time": 0.0}])
            self.assertEqual(response_data.json['lyrics'], "URL lyrics")
            self.assertEqual(response_data.json['aligned_lyrics'], ["Aligned G"])
            self.assertEqual(response_data.json['song_structure'], {"structure": ["Chorus"]})
            
            mock_get_chords.assert_called_once_with(url)
            mock_get_lyrics_from_url_or_metadata.assert_called_once_with(url=url)
            mock_check_audio_file.assert_not_called()
            mock_rmtree.assert_not_called()

    @patch('web_app.app.get_chords')
    @patch('web_app.app.check_audio_file', side_effect=ValueError("Invalid audio"))
    @patch('web_app.app.tempfile.mkdtemp', return_value='mock_temp_dir')
    @patch('web_app.app.shutil.rmtree')
    @patch('builtins.open', new_callable=MagicMock) # Mock open for FileStorage.save
    def test_process_chord_extraction_file_invalid_audio(self, mock_open, mock_rmtree, mock_mkdtemp, mock_check_audio_file, mock_get_chords):
        mock_audio_file = FileStorage(
            stream=MagicMock(), # Use MagicMock for stream
            filename='test_audio.txt',
            content_type='text/plain'
        )
        with app.app_context():
            with app.test_request_context():
                with patch('web_app.app.request') as mock_request:
                    mock_request.files = {'audio': mock_audio_file}
                    mock_request.files['audio'].filename = 'test_audio.txt'

                    response_data, status_code = process_chord_extraction(None, False)
                    
                    self.assertEqual(status_code, 400)
                    self.assertIn("Invalid file: Invalid audio", response_data.json['error'])
                    mock_rmtree.assert_called_once_with('mock_temp_dir')
                    mock_open.assert_called_once_with(os.path.join('mock_temp_dir', 'test_audio.txt'), 'wb')

    @patch('web_app.app.process_chord_extraction')
    def test_extract_chords_route(self, mock_process_chord_extraction):
        mock_process_chord_extraction.return_value = (jsonify({"chords": []}), 200)
        
        with app.app_context():
            with patch('web_app.app.request') as mock_request:
                mock_request.files = {'audio': MagicMock(spec=FileStorage)}
                response = self.app.post('/extract_chords', data={'audio': 'dummy'})
                
                self.assertEqual(response.status_code, 200)
                mock_process_chord_extraction.assert_called_once_with(None, False)

    @patch('web_app.app.process_chord_extraction')
    def test_extract_chords_from_url_route(self, mock_process_chord_extraction):
        mock_process_chord_extraction.return_value = (jsonify({"chords": []}), 200)
        
        with app.app_context():
            response = self.app.post('/extract_chords_from_url', json={'url': 'http://example.com/song.mp3'})
            
            self.assertEqual(response.status_code, 200)
            mock_process_chord_extraction.assert_called_once_with('http://example.com/song.mp3', True)

    @patch('web_app.app.get_chords_batch')
    @patch('web_app.app.check_audio_file')
    @patch('web_app.app.tempfile.mkdtemp', return_value='mock_batch_temp_dir')
    @patch('web_app.app.shutil.rmtree')
    def test_extract_chords_batch_route_success(self, mock_rmtree, mock_mkdtemp, mock_check_audio_file, mock_get_chords_batch):
        mock_get_chords_batch.return_value = {
            os.path.join('mock_batch_temp_dir', 'audio1.mp3'): [{"chord": "C"}],
            os.path.join('mock_batch_temp_dir', 'audio2.wav'): [{"chord": "G"}]
        }
        
        mock_audio1 = MagicMock(spec=FileStorage, filename='audio1.mp3')
        mock_audio2 = MagicMock(spec=FileStorage, filename='audio2.wav')
        
        with app.app_context():
            with patch('web_app.app.request') as mock_request:
                mock_request.files.getlist.return_value = [mock_audio1, mock_audio2]
                
                response = self.app.post('/extract_chords_batch', data={'audios': ['dummy1', 'dummy2']})
                
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {
                    'audio1.mp3': [{'chord': 'C'}],
                    'audio2.wav': [{'chord': 'G'}],
                })
                mock_get_chords_batch.assert_called_once()
                mock_rmtree.assert_called_once_with('mock_batch_temp_dir')

    @patch('web_app.app.transpose_chords')
    def test_transpose_route_success(self, mock_transpose_chords):
        mock_transpose_chords.return_value = ["D", "A", "Bm"]
        
        response = self.app.post('/transpose', json={
            "chords": [{"chord": "C", "time": 0.0}, {"chord": "G", "time": 1.0}, {"chord": "Am", "time": 2.0}],
            "semitones": 2
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['chords'], [
            {"chord": "D", "time": 0.0}, {"chord": "A", "time": 1.0}, {"chord": "Bm", "time": 2.0}
        ])
        mock_transpose_chords.assert_called_once_with(["C", "G", "Am"], 2)

    @patch('web_app.app.recommend_capo')
    def test_capo_route_success(self, mock_recommend_capo):
        mock_recommend_capo.return_value = (3, ["D", "A", "Bm"])
        
        response = self.app.post('/capo', json={
            "chords": [{"chord": "C", "time": 0.0}, {"chord": "G", "time": 1.0}, {"chord": "Am", "time": 2.0}]
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['capo'], 3)
        self.assertEqual(response.json['chords'], [
            {"chord": "D", "time": 0.0}, {"chord": "A", "time": 1.0}, {"chord": "Bm", "time": 2.0}
        ])
        mock_recommend_capo.assert_called_once_with(["C", "G", "Am"])

    @patch('web_app.app.apply_rule_based_flourishes')
    @patch('web_app.app.generate_magenta_flourish')
    @patch('web_app.app.suggest_chord_substitutions', new=MagicMock(name='gpt4all_suggest'))
    def test_flourish_route_rule_based(self, mock_gpt4all_suggest, mock_magenta, mock_rule_based):
        mock_rule_based.return_value = ["Cadd9", "G7"]
        
        with app.app_context():
            response = self.app.post('/flourish', json={
                "chords": [{"chord": "C", "time": 0.0}, {"chord": "G", "time": 1.0}],
                "method": "rule_based"
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['flourishes'], ["Cadd9", "G7"])
            mock_rule_based.assert_called_once_with([{"chord": "C", "time": 0.0}, {"chord": "G", "time": 1.0}], rule_set_name="default")
            mock_magenta.assert_not_called()
            mock_gpt4all_suggest.assert_not_called()

    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    def test_get_lyrics_route_success(self, mock_get_lyrics_from_url_or_metadata):
        mock_get_lyrics_from_url_or_metadata.return_value = {
            "lyrics_text": "Test lyrics", "method": "metadata"
        }
        with app.app_context():
            response = self.app.post('/get_lyrics', json={"title": "Song", "artist": "Artist"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['lyrics'], "Test lyrics")
            self.assertEqual(response.json['source'], "metadata")
            mock_get_lyrics_from_url_or_metadata.assert_called_once_with(url=None, title="Song", artist="Artist")

    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    def test_get_lyrics_route_azlyrics_failure(self, mock_get_lyrics_from_url_or_metadata):
        mock_get_lyrics_from_url_or_metadata.return_value = {
            "lyrics_text": "", "method": "scrape_azlyrics", "url": "http://example.com/azlyrics"
        }
        with app.app_context():
            response = self.app.post('/get_lyrics', json={"url": "http://example.com/azlyrics"})
            self.assertEqual(response.status_code, 500)
            self.assertIn("Failed to retrieve lyrics from AZLyrics.", response.json['error'])

    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    def test_get_lyrics_route_placeholder_url(self, mock_get_lyrics_from_url_or_metadata):
        mock_get_lyrics_from_url_or_metadata.return_value = {
            "lyrics_text": "Placeholder content", "method": "placeholder_url", "url": "http://example.com/placeholder"
        }
        with app.app_context():
            response = self.app.post('/get_lyrics', json={"url": "http://example.com/placeholder"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['lyrics'], "Placeholder content")
            self.assertEqual(response.json['source'], "placeholder_url")

    @patch('web_app.app.get_lyrics_from_url_or_metadata')
    def test_get_lyrics_route_missing_data(self, mock_get_lyrics_from_url_or_metadata):
        with app.app_context():
            response = self.app.post('/get_lyrics', json={})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Missing URL or song title/artist.", response.json['error'])
            mock_get_lyrics_from_url_or_metadata.assert_not_called()

    @patch('web_app.app.suggest_fingerings_lib')
    @patch('web_app.app.Fretboard') # Patch Fretboard constructor
    def test_suggest_fingerings_route_success(self, MockFretboard, mock_suggest_fingerings_lib):
        mock_shape = MagicMock(spec=ChordShape)
        mock_shape.name = "C Shape"
        mock_shape.template_root_note_str = "C"
        mock_shape.chord_type = "maj"
        mock_shape.base_fret_of_template = 0
        mock_shape.fingerings = [[0, 3, 1]]
        mock_shape.is_movable = False
        mock_shape.barre_strings_offset = None
        
        mock_suggest_fingerings_lib.return_value = [(mock_shape, 10)]

        with app.app_context():
            response = self.app.post('/suggest_fingerings', json={"chord_string": "C"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['chord'], "C")
            self.assertEqual(len(response.json['suggestions']), 1)
            self.assertEqual(response.json['suggestions'][0]['name'], "C Shape")
            self.assertEqual(response.json['suggestions'][0]['score'], 10)
            mock_suggest_fingerings_lib.assert_called_once_with("C", fretboard=MockFretboard.return_value)
            MockFretboard.assert_called_once_with(tuning=None) # Default tuning

if __name__ == '__main__':
    unittest.main()
