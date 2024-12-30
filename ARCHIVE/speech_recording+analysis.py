import os
import pyaudio
import wave
import speech_recognition as sr
import threading
from transformers import pipeline
import tkinter as tk

# Set the TOKENIZERS_PARALLELISM environment variable to false
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Parameters for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize recognizer
recognizer = sr.Recognizer()
audio = pyaudio.PyAudio()
stream = None
frames = []
is_recording = False

def start_recording():
    global stream, frames, is_recording
    is_recording = True
    frames = []
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")
    record_thread = threading.Thread(target=record)
    record_thread.start()

def record():
    global frames, is_recording
    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

def stop_recording():
    global stream, is_recording
    is_recording = False
    stream.stop_stream()
    stream.close()
    print("Finished recording.")
    save_audio()
    transcribed_text = transcribe_audio()
    if transcribed_text:
        # Create threads for summarization and sentiment analysis
        summarize_thread = threading.Thread(target=summarize_text, args=(transcribed_text,))
        sentiment_thread = threading.Thread(target=sentiment_analysis, args=(transcribed_text,))

        # Start threads
        summarize_thread.start()
        sentiment_thread.start()

        # Wait for threads to complete
        summarize_thread.join()
        sentiment_thread.join()
    print("Processing complete.")

def save_audio():
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print("Audio saved.")

def transcribe_audio():
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print("Transcription: " + text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return None

def summarize_text(text):
    summarizer = pipeline("summarization", model='sshleifer/distilbart-cnn-12-6', device=-1)
    # Adjust max_length and min_length based on the length of the input text
    input_length = len(text.split())
    max_length = min(50, input_length // 2)
    min_length = min(10, max_length - 1)
    if max_length < 1:
        max_length = 1
    if min_length < 1:
        min_length = 1
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    print("Summary: " + summary[0]['summary_text'])

def sentiment_analysis(text):
    classifier = pipeline("sentiment-analysis", model='distilbert-base-uncased-finetuned-sst-2-english', device=-1)
    result = classifier(text)
    print("Sentiment: " + result[0]['label'])

# Create the GUI
root = tk.Tk()
root.title("Audio Recorder")

record_button = tk.Button(root, text="Record", command=start_recording)
record_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_recording)
stop_button.pack(pady=10)

root.mainloop()

# Ensure proper cleanup
audio.terminate()
print("Script finished.")