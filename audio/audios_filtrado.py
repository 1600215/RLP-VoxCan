import spidev
import time
import numpy as np
import signal
import sys
from scipy.signal import butter, lfilter
from pydub import AudioSegment
import wave

# Inicializar SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus SPI 0, dispositivo CS 0
spi.max_speed_hz = 1350000  # Velocidad máxima del bus SPI

# Parámetros de grabación
sample_rate = 4000  # Frecuencia de muestreo (Hz)
num_samples = sample_rate * 10  # Número de muestras a grabar (10 segundos por defecto)

# Almacenar las lecturas del canal
samples = []

# Función para leer un canal del MCP3008
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Función para manejar la interrupción
def signal_handler(sig, frame):
    print("\nInterrupción recibida, guardando el archivo...")
    save_audio_file(samples)
    spi.close()
    sys.exit(0)

# Función de filtrado de paso bajo para eliminar ruido
def low_pass_filter(data, cutoff=1000, fs=8000, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y


# Función para guardar los datos en un archivo MP3
def save_audio_file(samples, file_index):
    output_file = f"audio_{file_index}.mp3"
    # Convertir las muestras a un rango de -32768 a 32767 para WAV
    samples = np.array(samples)
    samples = (samples - np.mean(samples)) / np.max(np.abs(samples))  # Normalizar
    samples = (samples * 32767).astype(np.int16)

    # Aplicar filtro de paso bajo para eliminar ruido
    filtered_samples = low_pass_filter(samples)

    # Guardar como WAV temporalmente
    temp_wav_file = "temp_audio.wav"
    with wave.open(temp_wav_file, 'w') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes (16 bits)
        wf.setframerate(sample_rate)
        wf.writeframes(filtered_samples.tobytes())

    # Convertir de WAV a MP3 usando pydub y cambiar velocidad
    audio = AudioSegment.from_wav(temp_wav_file)
    audio.export(output_file, format="mp3")
    print(f"Archivo guardado: {output_file}")

# Registrar la función de manejo de señal
signal.signal(signal.SIGINT, signal_handler)

def record_audio_segment():
    file_index = 1
    while True:
        samples.clear()
        while len(samples) < num_samples:
            value = read_channel(0)
            samples.append(value)
            time.sleep(1.0 / sample_rate)  # Ajustar el intervalo de muestreo

        save_audio_file(samples, file_index)
        file_index += 1

        # Esperar 10 segundos antes de grabar el siguiente segmento
        time.sleep(10)

if __name__ == "__main__":
    print("MCP3008 audio recording test.")
    record_audio_segment()