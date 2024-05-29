import spidev
import wave
import os
import time
import signal

# Crea un objeto SPI
spi = spidev.SpiDev()

# Abre el bus SPI
spi.open(0, 0)

# Ruta al directorio de salida
base_output_dir = os.path.join(os.path.dirname(__file__), 'out')

# Verifica si el directorio de salida existe, si no, créalo
if not os.path.exists(base_output_dir):
    os.makedirs(base_output_dir)

# Función para crear directorios si no existen
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Configura el archivo de log
log_file_path = os.path.join(base_output_dir, 'log.txt')

# Definir subdirectorios para cada tipo de dato
subdirs = ['int', 'float', 'byte', 'unsigned_int', 'string', 'percentage']
for subdir in subdirs:
    create_directory(os.path.join(base_output_dir, subdir))

def read_channel(channel):
    try:
        # Envía una cadena de comandos al MCP3008
        command = [0b00000001, (0b1000 + channel) << 4, 0b00000000]
        response = spi.xfer2(command)

        # Procesa la respuesta
        adc = ((response[1] & 0b11) << 8) + response[2]
        return adc
    except Exception as e:
        print(f"Error leyendo el canal SPI: {e}")
        return None

# Función para registrar diferentes interpretaciones del valor leído
def log_value(value, file):
    try:
        int_value = int(value)
        float_value = float(value)
        byte_value = value.to_bytes(2, 'little')
        unsigned_int_value = value & 0xFFFF
        string_value = str(value)
        percent_value = (value / 1023.0) * 100  # Asumiendo un ADC de 10 bits

        file.write(f"Valor leído: {value}\n")
        file.write(f"Interpretación como entero: {int_value}\n")
        file.write(f"Interpretación como flotante: {float_value}\n")
        file.write(f"Interpretación como bytes: {byte_value}\n")
        file.write(f"Bytes en formato hexadecimal: {byte_value.hex()}\n")
        file.write(f"Interpretación como entero sin signo: {unsigned_int_value}\n")
        file.write(f"Interpretación como cadena de caracteres: {string_value}\n")
        file.write(f"Interpretación como porcentaje: {percent_value:.2f}%\n")
        file.write("\n")
    except Exception as e:
        file.write(f"Error en la interpretación del valor: {e}\n")
        file.write("\n")

# Función para inicializar archivos de audio
def initialize_audio_files(file_number):
    int_path = os.path.join(base_output_dir, 'int', f'audio_{file_number}.wav')
    float_path = os.path.join(base_output_dir, 'float', f'audio_{file_number}.wav')
    byte_path = os.path.join(base_output_dir, 'byte', f'audio_{file_number}.wav')
    unsigned_int_path = os.path.join(base_output_dir, 'unsigned_int', f'audio_{file_number}.wav')
    string_path = os.path.join(base_output_dir, 'string', f'audio_{file_number}.wav')
    percentage_path = os.path.join(base_output_dir, 'percentage', f'audio_{file_number}.wav')

    int_file = wave.open(int_path, 'w')
    float_file = wave.open(float_path, 'w')
    byte_file = wave.open(byte_path, 'w')
    unsigned_int_file = wave.open(unsigned_int_path, 'w')
    string_file = wave.open(string_path, 'w')
    percentage_file = wave.open(percentage_path, 'w')

    for audio_file in [int_file, float_file, byte_file, unsigned_int_file, string_file, percentage_file]:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(44100)
    
    return int_file, float_file, byte_file, unsigned_int_file, string_file, percentage_file

# Función para cerrar archivos de audio
def close_audio_files(audio_files):
    for audio_file in audio_files:
        audio_file.close()

# Función para escribir los datos en archivos de audio
def write_audio_files(value, audio_files):
    try:
        int_file, float_file, byte_file, unsigned_int_file, string_file, percentage_file = audio_files
        
        int_file.writeframes(value.to_bytes(2, 'little'))
        float_file.writeframes(int(float(value)).to_bytes(2, 'little'))
        byte_file.writeframes(value.to_bytes(2, 'little'))
        unsigned_int_file.writeframes((value & 0xFFFF).to_bytes(2, 'little'))
        string_file.writeframes(int(value).to_bytes(2, 'little'))
        percentage_file.writeframes(int((value / 1023.0) * 100 * 1023 / 100).to_bytes(2, 'little'))
            
    except Exception as e:
        print(f"Error escribiendo archivos de audio: {e}")

# Configura el archivo de audio
sample_rate = 44100  # Frecuencia de muestreo, ajusta esto si es necesario
num_channels = 1  # Número de canales (1 para mono)
sample_width = 2  # Ancho de muestra en bytes

# Manejo de señal para cerrar archivos correctamente al detener el script
def signal_handler(sig, frame):
    print('Deteniendo el script y cerrando archivos de audio...')
    close_audio_files(audio_files)
    spi.close()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

file_number = 0
audio_files = initialize_audio_files(file_number)

# Bucle principal para grabar datos continuamente
print("Comenzando la grabación. Presiona Ctrl+C para detener.")
while True:
    try:
        value = read_channel(0)
        if value is not None:
            # Escribir datos en archivos de audio
            write_audio_files(value, audio_files)

            # Registrar el valor leído y sus interpretaciones
            with open(log_file_path, 'a') as log_file:
                log_value(value, log_file)

            # Debug: Mostrar el valor leído
            print(f"Valor leído: {value}")
        else:
            print("No se recibió valor del canal SPI")
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        break
