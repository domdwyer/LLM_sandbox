import os
import pyaudio
import wave
import threading
from datetime import datetime
import signal
import sys
import whisper

# Set the TOKENIZERS_PARALLELISM environment variable to false
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Initialize recognizer and audio variables
audio = pyaudio.PyAudio()
stream = None
frames = []
is_recording = False

# Ensure the OUTPUTS directory exists
OUTPUT_DIR = "OUTPUTS"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M")

def start_recording():
    global stream, frames, is_recording
    is_recording = True
    frames = []
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

def stop_recording():
    global stream, is_recording
    is_recording = False
    stream.stop_stream()
    stream.close()
    print("Finished recording.")
    timestamp = get_timestamp()
    wave_output_filename = os.path.join(OUTPUT_DIR, f"output_{timestamp}.wav")
    transcript_output_filename = os.path.join(OUTPUT_DIR, f"transcript_{timestamp}.txt")
    save_audio(wave_output_filename)
    transcribed_text = transcribe_audio_whisper(wave_output_filename)
    if transcribed_text:
        with open(transcript_output_filename, "w") as f:
            f.write(transcribed_text)
    print("Processing complete.")

def save_audio(filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved as {filename}.")

def transcribe_audio_whisper(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    text = result["text"]
    print("Transcription: " + text)
    return text

def record_thread():
    start_recording()

def signal_handler(sig, frame):
    if is_recording:
        stop_recording()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        print("Press Enter to start recording...")
        input()
        recording_thread = threading.Thread(target=record_thread)
        recording_thread.start()
        print("Press Enter to stop recording...")
        input()
        stop_recording()
        recording_thread.join(timeout=1)  # Ensure the thread exits properly
    finally:
        audio.terminate()
        print("Script finished.")