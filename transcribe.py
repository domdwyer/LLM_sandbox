import os
import sys
import subprocess
import warnings
import whisper

# Suppress specific warnings from Whisper or PyTorch
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", category=FutureWarning, message="You are using `torch.load` with `weights_only=False`")

def check_ffmpeg():
    """
    Checks whether ffmpeg is installed and available on the system PATH.
    Exits with status 1 if ffmpeg is missing or throws an error.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("ffmpeg is installed and available.")
    except FileNotFoundError:
        # ffmpeg was not found at all in PATH
        print("ffmpeg is not installed or not available in the system's PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        # ffmpeg exists but returned an error
        print("ffmpeg is installed but returned an error.")
        sys.exit(1)

def transcribe_audio_whisper(filename):
    """
    Loads the Whisper model and transcribes the given audio file.
    Returns the transcribed text as a string.
    """
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    text = result["text"]
    print("Transcription: " + text)
    return text

def main(audio_files):
    """
    Orchestrates the transcription process:
    1. Checks ffmpeg availability.
    2. Iterates over provided audio files, skipping any that don't exist.
    3. Transcribes valid audio files and writes transcripts to .txt files (even if empty).
    """
    check_ffmpeg()

    for audio_file in audio_files:
        if not os.path.exists(audio_file):
            print(f"File {audio_file} does not exist.")
            continue

        transcript_output_filename = os.path.splitext(audio_file)[0] + ".txt"

        # Even if Whisper returns an empty string, we'll still create the transcript file
        transcribed_text = transcribe_audio_whisper(audio_file)

        # Always write the transcript file
        with open(transcript_output_filename, "w") as f:
            f.write(transcribed_text)

        print(f"Transcript saved as {transcript_output_filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <path_to_audio_file1> <path_to_audio_file2> ...")
    else:
        main(sys.argv[1:])