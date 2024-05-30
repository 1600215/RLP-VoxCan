import sounddevice as sd
import numpy as np
import wave
import keyboard
import datetime
import threading

def save_audio(audio_data, samplerate=44100):
    # Genera un nombre de archivo basado en la fecha y hora actual
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"audio_{current_time}.wav"

    # Guarda los datos en un archivo WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes (16 bits)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    print(f"Audio guardado como '{filename}'.")

def record_audio():
    # Lista para almacenar los fragmentos de audio
    audio_data = []

    def callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    # Inicia la grabación continua
    with sd.InputStream(samplerate=44100, channels=1, dtype='int16', callback=callback):
        print("Grabando audio continuamente... Presiona Ctrl+S para guardar y comenzar una nueva grabación. Presiona Ctrl+C para detener.")
        
        while True:
            sd.sleep(100)
            if keyboard.is_pressed('ctrl+s'):
                # Combina los fragmentos de audio en un solo array
                audio_data_combined = np.concatenate(audio_data, axis=0)
                # Guarda la grabación actual
                save_audio(audio_data_combined)
                # Reinicia la lista para la nueva grabación
                audio_data = []
                print("Nueva grabación iniciada...")
            if keyboard.is_pressed('ctrl+c'):
                print("Proceso detenido.")
                break

if __name__ == "__main__":
    record_audio()
