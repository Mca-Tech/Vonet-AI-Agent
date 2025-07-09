# /core/tts_handler.py

import os
import subprocess
import time
import threading
import winsound
import config

def start_piper_tts():
    """Initializes and starts the Piper TTS engine process."""
    piper_path = config.resource_path(r"piper\piper")
    piper_onnx = config.resource_path(r"piper\en_US-hfc_female-medium.onnx")
    piper_audios = config.resource_path(r"piper\audios")
    os.makedirs(piper_audios, exist_ok=True)
    
    print("Starting Piper TTS engine...")
    config.piper_process = subprocess.Popen(
        [piper_path, "-m", piper_onnx, "-d", piper_audios],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )

def get_all_audio_files(directory):
    """Gets all .wav files in a directory, sorted by modification time."""
    wav_files = [f for f in os.listdir(directory) if f.endswith(".wav")]
    if not wav_files:
        return []
    sorted_files = sorted(wav_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    return [os.path.join(directory, f) for f in sorted_files]

def text_to_speech(text):
    """Converts text to speech in a separate thread to avoid blocking the GUI."""
    config.TTS_SPEAKING = True
    
    def tts_thread():
        try:
            audio_dir = config.resource_path(r"piper\audios")
            speaking_flag = config.resource_path(r"piper\speaking.txt")

            # Clear old audio files and flag
            for filename in os.listdir(audio_dir):
                os.remove(os.path.join(audio_dir, filename))
            if os.path.exists(speaking_flag):
                os.remove(speaking_flag)

            # Send text to Piper and create speaking flag
            config.piper_process.stdin.write(text + "\n")
            config.piper_process.stdin.flush()
            with open(speaking_flag, "w") as f:
                f.write("speaking")

            def play_audio_sequence():
                # Wait for audio files to be generated
                while True:
                    audio_files = get_all_audio_files(audio_dir)
                    if not audio_files:
                        if not os.path.exists(speaking_flag): return
                    else:
                        if os.path.exists(speaking_flag): os.remove(speaking_flag)
                        break
                    time.sleep(0.1)

                # Play generated audio files in order
                for i, audio_file in enumerate(audio_files):
                    new_name = os.path.join(audio_dir, f"{i}.wav")
                    while True:
                        try:
                            os.rename(audio_file, new_name)
                            if config.app_instance:
                                config.app_instance.after(0, config.app_instance.loading, "start", "")
                            winsound.PlaySound(new_name, winsound.SND_FILENAME)
                            if config.app_instance:
                                config.app_instance.after(0, config.app_instance.loading, "end", "")
                            os.remove(new_name)
                            break
                        except (IOError, PermissionError):
                            time.sleep(0.1)
                play_audio_sequence()

            play_audio_sequence()
        except Exception as e:
            print(f"TTS Exception: {e}")
        finally:
            config.TTS_SPEAKING = False

    threading.Thread(target=tts_thread, daemon=True).start()