import spidev
import time
import numpy as np
import signal
import sys
from pydub import AudioSegment
import wave
from datetime import datetime

# Inicializar SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus SPI 0, dispositivo CS 0
spi.max_speed_hz = 1350000  # Velocidad máxima del bus SPI

# Parámetros de grabación
sample_rate = 4000  # Frecuencia de muestreo (Hz)
num_samples = sample_rate * 10  # Número de muestras a grabar (10 segundos por defecto)

# Almacenar las lecturas de los canales
samples = {0: [], 1: [], 7: []}

# Función para leer un canal del MCP3008
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Función para manejar la interrupción
def signal_handler(sig, frame):
    print("\nInterrupción recibida, guardando los archivos...")
    for channel in samples:
        save_audio_file(samples[channel], channel)
    spi.close()
    sys.exit(0)

# Función para guardar los datos en un archivo MP3
def save_audio_file(samples, channel):
    # Obtener el tiempo actual para el nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"audio_channel_{channel}_{timestamp}.mp3"

    # Convertir las muestras a un rango de -32768 a 32767 para WAV
    samples = np.array(samples)
    samples = (samples - np.mean(samples)) / np.max(np.abs(samples))  # Normalizar
    samples = (samples * 32767).astype(np.int16)

    # Guardar como WAV temporalmente
    temp_wav_file = f"temp_audio_channel_{channel}.wav"
    with wave.open(temp_wav_file, 'w') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes (16 bits)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())

    # Convertir de WAV a MP3 usando pydub
    audio = AudioSegment.from_wav(temp_wav_file)
    audio.export(output_file, format="mp3")
    print(f"Archivo guardado: {output_file}")

# Registrar la función de manejo de señal
signal.signal(signal.SIGINT, signal_handler)

def main():
    print("MCP3008 audio recording test.")

    while True:
        # Limpiar las muestras anteriores
        for channel in samples:
            samples[channel].clear()
        
        # Grabar nuevas muestras
        while len(samples[0]) < num_samples and len(samples[1]) < num_samples and len(samples[7]) < num_samples:
            for channel in samples:
                value = read_channel(channel)
                samples[channel].append(value)

            time.sleep(1.0 / sample_rate)  # Ajustar el intervalo de muestreo

        # Esperar 10 segundos antes de grabar el siguiente segmento
        time.sleep(10)

if __name__ == "__main__":
    main()
