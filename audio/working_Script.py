import spidev
import time
import wave
import numpy as np
import signal
import sys

# Inicializar SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus SPI 0, dispositivo CS 0
spi.max_speed_hz = 1350000  # Velocidad máxima del bus SPI

# Parámetros de grabación
sample_rate = 8000  # Frecuencia de muestreo (Hz)
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

# Función para guardar los datos en un archivo WAV
def save_audio_file(samples):
    output_file = "audio.wav"
    # Convertir las muestras a un rango de -32768 a 32767 para WAV
    samples = np.array(samples)
    samples = (samples - np.mean(samples)) / np.max(np.abs(samples))  # Normalizar
    samples = (samples * 32767).astype(np.int16)
    
    with wave.open(output_file, 'w') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes (16 bits)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    print(f"Archivo guardado: {output_file}")

# Registrar la función de manejo de señal
signal.signal(signal.SIGINT, signal_handler)

def main():
    print("MCP3008 audio recording test.")
    start_time = time.time()
    
    while True:
        value = read_channel(0)
        samples.append(value)
        if len(samples) >= num_samples:
            print("\nSe ha alcanzado el número máximo de muestras.")
            break
        time.sleep(1.0 / sample_rate)  # Ajustar el intervalo de muestreo

    save_audio_file(samples)

if __name__ == "__main__":
    main()

