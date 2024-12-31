import unittest
import os
import sys
from transcribe import check_ffmpeg, transcribe_audio_whisper, main

class TestTranscribe(unittest.TestCase):

    def test_check_ffmpeg_installed(self):
        """Test that ffmpeg is correctly detected when installed."""
        try:
            check_ffmpeg()  # Should pass if ffmpeg is installed on this system
        except SystemExit:
            self.fail("check_ffmpeg() raised SystemExit unexpectedly!")

    def test_check_ffmpeg_not_installed(self):
        """Test that check_ffmpeg exits gracefully when ffmpeg is not available."""
        # Temporarily modify PATH to simulate ffmpeg not being installed
        original_path = os.environ["PATH"]
        os.environ["PATH"] = ""
        try:
            with self.assertRaises(SystemExit):
                check_ffmpeg()
        finally:
            os.environ["PATH"] = original_path  # Restore the original PATH

    def test_transcribe_audio_whisper(self):
        """Test transcribe_audio_whisper with a small real audio file (test.wav)."""
        audio_file = "test.wav"
        if not os.path.exists(audio_file):
            self.skipTest(f"No {audio_file} file found. Add one for this test.")

        # Run the transcription
        result = transcribe_audio_whisper(audio_file)

        # Validate the transcription result
        self.assertIsInstance(result, str, "Transcription should return a string.")
        self.assertGreater(len(result), 0, "Transcription result should not be empty.")

    def test_main(self):
        """Test main function with one existing file and one missing file."""
        # Create a dummy audio file
        audio_file = "test_dummy.wav"
        transcript_file = "test_dummy.txt"
        with open(audio_file, "w") as f:
            f.write("dummy audio content")  # Dummy content for testing

        try:
            # Run main
            main([audio_file, "missing_file.wav"])

            # Check if the transcript file is created
            self.assertTrue(
                os.path.exists(transcript_file),
                f"{transcript_file} was not created by transcribe.py"
            )

            # Verify the transcript is non-empty
            with open(transcript_file, "r") as f:
                content = f.read()
                self.assertGreater(len(content), 0, "Transcript file should not be empty.")

        finally:
            # Cleanup
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(transcript_file):
                os.remove(transcript_file)

if __name__ == "__main__":
    unittest.main()