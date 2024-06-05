import os
import time
from pydub.generators import Sine

# Configura la carpeta de destino
AUDIO_FOLDER = './uploads'  # Cambia esto por la ruta de tu carpeta de destino

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def generate_mp3(filename):
    duration = 1000  # duración del archivo en milisegundos
    sine_wave = Sine(440).to_audio_segment(duration=duration)
    sine_wave.export(filename, format="mp3")
    print(f"Archivo generado: {filename}")

while True:
    timestamp = int(time.time())
    filename = os.path.join(AUDIO_FOLDER, f"{timestamp}.mp3")
    generate_mp3(filename)
    time.sleep(5)  # Espera 5 segundos antes de generar el siguiente archivo
