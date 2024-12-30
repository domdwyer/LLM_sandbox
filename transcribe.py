import os
import whisper
import sys
import subprocess
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", category=FutureWarning, message="You are using `torch.load` with `weights_only=False`")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ffmpeg is installed and available.")
    except subprocess.CalledProcessError:
        print("ffmpeg is not installed or not available in the system's PATH.")
        exit(1)

def transcribe_audio_whisper(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    text = result["text"]
    print("Transcription: " + text)
    return text

def main(audio_files):
    check_ffmpeg()

    for audio_file in audio_files:
        if not os.path.exists(audio_file):
            print(f"File {audio_file} does not exist.")
            continue

        transcript_output_filename = os.path.splitext(audio_file)[0] + ".txt"
        transcribed_text = transcribe_audio_whisper(audio_file)
        if transcribed_text:
            with open(transcript_output_filename, "w") as f:
                f.write(transcribed_text)
            print(f"Transcript saved as {transcript_output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <path_to_audio_file1> <path_to_audio_file2> ...")
    else:
        main(sys.argv[1:])