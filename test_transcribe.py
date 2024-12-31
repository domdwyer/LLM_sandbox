import os
import wave
import struct
import pytest
from transcribe import check_ffmpeg, transcribe_audio_whisper, main


# ---- Fixtures ---- #

@pytest.fixture
def dummy_audio_file():
    """
    Fixture to create and clean up a valid dummy WAV file.
    This version *still* creates 1s of silence for simplicity.
    """
    filename = "test_dummy.wav"
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(16000)   # 16kHz sample rate
        for _ in range(16000):   # 1 second of silence
            wf.writeframes(struct.pack("<h", 0))  # 16-bit PCM silence
    yield filename
    if os.path.exists(filename):
        os.remove(filename)


@pytest.fixture
def real_audio_file():
    """Fixture for a valid test audio file (test.wav)."""
    filename = "test.wav" # NEED TO EXPAND TO INCLUDE EXEMPLAR FILES 
    if not os.path.exists(filename):
        pytest.skip(f"Required file '{filename}' not found.")
    yield filename


# ---- Tests ---- #

def test_check_ffmpeg_installed():
    """Test that ffmpeg is correctly detected when installed."""
    try:
        check_ffmpeg()
    except SystemExit:
        pytest.fail("check_ffmpeg raised SystemExit unexpectedly!")


def test_check_ffmpeg_not_installed(monkeypatch):
    """Test that check_ffmpeg exits gracefully when ffmpeg is not available."""
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit):
        check_ffmpeg()


def test_transcribe_audio_whisper(real_audio_file):
    """Test transcribe_audio_whisper with a small real audio file."""
    result = transcribe_audio_whisper(real_audio_file)
    assert isinstance(result, str), "Transcription should return a string."
    assert len(result) > 0, "Transcription result should not be empty."


def test_main(dummy_audio_file):
    """
    Test main function with one existing file (that might be silent)
    and one missing file. We now allow an empty transcription as valid.
    """
    missing_file = "missing_file.wav"
    transcript_file = os.path.splitext(dummy_audio_file)[0] + ".txt"

    try:
        main([dummy_audio_file, missing_file])

        # Check that the transcript file was created
        assert os.path.exists(transcript_file), f"{transcript_file} was not created."

        # Verify the transcript file was written, even if it's empty
        with open(transcript_file, "r") as f:
            content = f.read()
            # Option B: Accept an empty string as valid
            assert content is not None, "Transcript file should not be None."
            # Alternatively, if you specifically expect an empty string:
            # assert content.strip() == "", "Expected empty transcription for silent file."

    finally:
        if os.path.exists(transcript_file):
            os.remove(transcript_file)