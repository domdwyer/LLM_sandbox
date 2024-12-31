from unittest.mock import patch, mock_open, MagicMock
import unittest
import subprocess
import os
import sys
from transcribe import check_ffmpeg, transcribe_audio_whisper, main

class TestTranscribe(unittest.TestCase):
    @patch("subprocess.run")
    def test_check_ffmpeg_installed(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(returncode=0)
        check_ffmpeg()

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ffmpeg", "ffmpeg not found"))
    def test_check_ffmpeg_not_installed(self, mock_subprocess_run):
        with self.assertRaises(SystemExit):
            check_ffmpeg()

    @patch("whisper.load_model")
    def test_transcribe_audio_whisper(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello, world!"}
        mock_load_model.return_value = mock_model
        result = transcribe_audio_whisper("dummy_audio_file.wav")
        self.assertEqual(result, "Hello, world!")

    @patch("builtins.open", new_callable=mock_open)   # <-- Note we patch builtins.open
    @patch("transcribe.os.path.exists")
    @patch("transcribe.transcribe_audio_whisper")
    def test_main(self, mock_transcribe, mock_exists, mock_file_open):
        mock_exists.side_effect = lambda fname: fname == "existing_file.wav"
        mock_transcribe.return_value = "Test transcription"

        with patch("transcribe.check_ffmpeg"):
            main(["existing_file.wav", "missing_file.wav"])

        mock_transcribe.assert_called_once_with("existing_file.wav")
        # We expect open(...) to be called once for existing_file.txt
        mock_file_open.assert_called_once_with("existing_file.txt", "w")
        # The write method should be called once
        mock_file_open().write.assert_called_once_with("Test transcription")

if __name__ == "__main__":
    unittest.main()