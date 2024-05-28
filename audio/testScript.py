import spidev
import wave
import os
import time

# Crea un objeto SPI
spi = spidev.SpiDev()

# Abre el bus SPI
spi.open(0, 0)

# Ruta al directorio de salida
output_dir = os.path.join(os.path.dirname(__file__), 'out')

# Verifica si el directorio de salida existe, si no, créalo
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def read_channel(channel):
    try:
        # Envía una cadena de comandos al MCP3008
        # 1. Comienza la transmisión (0b00000001)
        # 2. Envía el número de canal
        # 3. Envía un byte vacío (0b00000000)
        command = [0b00000001, (0b1000 + channel) << 4, 0b00000000]
        response = spi.xfer2(command)

        # Procesa la respuesta
        # 1. Ignora el primer byte de la respuesta.
        # 2. Toma los 2 últimos bits del segundo byte y los une con el tercer byte
        adc = ((response[1] & 0b11) << 8) + response[2]
        return adc
    except Exception as e:
        print(f"Error leyendo el canal SPI: {e}")
        return None


# Configura el archivo de audio
sample_rate = 44100  # Frecuencia de muestreo, ajusta esto si es necesario
num_channels = 1  # Número de canales (1 para mono)
sample_width = 2  # Ancho de muestra en bytes

start_time = time.time()
file_number = 0

while True:
    # Crea un nuevo archivo cada 15 segundos
    if time.time() - start_time >= 15:
        start_time = time.time()
        file_number += 1

    # Abre el archivo en modo de escritura
    file_path = os.path.join(output_dir, f'audio_{file_number}.wav')
    print(f"Creando archivo: {file_path}")
    try:
        with wave.open(file_path, 'w') as audio_file:
            audio_file.setnchannels(num_channels)
            audio_file.setsampwidth(sample_width)
            audio_file.setframerate(sample_rate)

            # Lee y escribe en el archivo durante 15 segundos
            end_time = start_time + 15
            while time.time() < end_time:
                value = read_channel(0)
                if value is not None:
                    audio_file.writeframes(
                        value.to_bytes(sample_width, 'little'))
                    # Debug: Mostrar el valor leído
                    print(f"Valor leído: {value}")
                else:
                    print("No se recibió valor del canal SPI")
    except Exception as e:
        print(f"Error escribiendo el archivo de audio: {e}")
