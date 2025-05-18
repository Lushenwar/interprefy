"""
================================================================================
 Transcriber - System Audio Capture and Speech-to-Text for Interprefy
================================================================================

This class is responsible for:
    - Capturing system audio using PyAudio from the VB-CABLE virtual device.
    - Saving audio chunks as temporary WAV files.
    - Transcribing audio to text using the faster-whisper model.
    - Passing the transcribed text (and optionally translation) to a callback.
    - Running audio capture and upload in background threads.

Note: Translation should be handled in AppController for clean separation.
"""

import threading
import pyaudio
import numpy as np
import wave
import time
import os
import queue
import datetime
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from model.Translator import Translator
from model.ProfileSettings import ProfileSettings
from view.SubtitleWindow import SubtitleWindow
from PyQt5.QtCore import QTimer

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
DEVICE_RATE = 48000
TARGET_RATE = 16000
RECORD_SECONDS = 5

class Transcriber:
    """
    Handles system audio capture and transcription.
    """
    def __init__(self, api_key=None, language="en", on_transcript=None, profile_settings=None):
        self.current_history_path = None
        self.language = language
        self.on_transcript = on_transcript  # Callback for delivering transcript (and translation)
        self.profile_settings = profile_settings or ProfileSettings()
        self.translator = Translator(self.profile_settings)
        self.audio_interface = pyaudio.PyAudio()
        self.running = False
        self.thread = None
        self.audio_queue = queue.Queue()
        self.upload_thread = None
        # Load Whisper model once for efficiency
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

    def _find_vbcable_device(self):
        # Find the VB-CABLE virtual audio device for system audio capture
        for i in range(self.audio_interface.get_device_count()):
            dev = self.audio_interface.get_device_info_by_index(i)
            name = dev.get('name', '').lower()
            if "cable output" in name and "virtual cable" in name and dev.get('maxInputChannels', 0) == 2:
                print(f"[VB-CABLE] Using device: {dev['name']}")
                return i
        raise RuntimeError("VB-CABLE device not found.")

    def _save_wav(self, filename, audio_data):
        # Save raw audio data as a mono WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio_interface.get_sample_size(FORMAT))
            wf.setframerate(TARGET_RATE)
            wf.writeframes(audio_data)

    def _transcribe_whisper(self, wav_path):
        # Transcribe audio file to text using Whisper
        segments, info = self.whisper_model.transcribe(wav_path)
        transcript = ""
        for segment in segments:
            transcript += segment.text.strip() + " "
        return transcript.strip()

    def _record_loop(self):
        # Main loop for audio capture and transcription
        device_index = self._find_vbcable_device()
        stream = self.audio_interface.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=DEVICE_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        self.running = True
        print("[Recorder] Recording from VB-CABLE every 5 seconds...")

        def uploader():
            # Handles processing and transcription of audio chunks in a background thread
            while self.running or not self.audio_queue.empty():
                try:
                    filename, raw_audio = self.audio_queue.get(timeout=1)
                except queue.Empty:
                    continue
                self._save_wav(filename, raw_audio)
                try:
                    transcript = self._transcribe_whisper(filename)
                    if transcript and self.on_transcript:
                        translated = self.translator.translate(transcript)
                        self._append_to_history(transcript, translated)
                        # Call the callback with transcript and translation
                        def safe_callback():
                            try:
                                self.on_transcript(transcript, translated)
                            except Exception as e:
                                print(f"[Transcriber Callback Error] {e}")
                        QTimer.singleShot(0, safe_callback)
                except Exception as e:
                    print(f"[Error] {e}")
                finally:
                    if os.path.exists(filename):
                        os.remove(filename)

            translated = self.translator.translate(transcript)
            self._append_to_history(transcript, translated)

        # Start uploader thread
        self.upload_thread = threading.Thread(target=uploader, daemon=True)
        self.upload_thread.start()

        # Main audio capture loop
        while self.running:
            frames = []
            for _ in range(0, int(DEVICE_RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_array = np.frombuffer(data, dtype=np.int16).reshape(-1, 2)
                mono = audio_array.mean(axis=1).astype(np.int16)
                resampled = resample_poly(mono, TARGET_RATE, DEVICE_RATE).astype(np.int16)
                frames.append(resampled.tobytes())
            raw_audio = b''.join(frames)
            filename = f"temp_{int(time.time()*1000)}.wav"
            self.audio_queue.put((filename, raw_audio))

        stream.stop_stream()
        stream.close()
        self.audio_interface.terminate()
        print("[Recorder] Stopped.")
        self.view.subtitle_window.label.setHidden(True)


    def start(self):
        # Create a new history file for this session
        date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs("history", exist_ok=True)
        self.current_history_path = os.path.join("history", f"history_{date_time}.txt")
        with open(self.current_history_path, "w", encoding="utf-8") as f:
            f.write("")  # Start with an empty file

        # Start the recording and transcription process in a background thread
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()


    def stop(self):
        # Stop recording and wait for threads to finish
        self.running = False
        if self.thread:
            self.thread.join()
        if self.upload_thread:
            self.upload_thread.join()

    import datetime

    def _append_to_history(self, original_text, translated_text):
        if not self.current_history_path:
            return  # Fail silently if no file is initialized
        with open(self.current_history_path, "a", encoding="utf-8") as f:
            print(original_text)
            print(translated_text)
            f.write(original_text.strip() + "\n")
            f.write(translated_text.strip() + "\n")
