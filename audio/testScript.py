import spidev
import wave
import os
import time

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

# Función para escribir los datos en archivos de audio
def write_audio_files(value, file_number):
    int_path = os.path.join(base_output_dir, 'int', f'audio_{file_number}.wav')
    float_path = os.path.join(base_output_dir, 'float', f'audio_{file_number}.wav')
    byte_path = os.path.join(base_output_dir, 'byte', f'audio_{file_number}.wav')
    unsigned_int_path = os.path.join(base_output_dir, 'unsigned_int', f'audio_{file_number}.wav')
    string_path = os.path.join(base_output_dir, 'string', f'audio_{file_number}.wav')
    percentage_path = os.path.join(base_output_dir, 'percentage', f'audio_{file_number}.wav')

    try:
        # Abrir y escribir en los archivos de audio
        with wave.open(int_path, 'w') as int_file, \
             wave.open(float_path, 'w') as float_file, \
             wave.open(byte_path, 'w') as byte_file, \
             wave.open(unsigned_int_path, 'w') as unsigned_int_file, \
             wave.open(string_path, 'w') as string_file, \
             wave.open(percentage_path, 'w') as percentage_file:
            
            # Configurar parámetros de los archivos de audio
            for audio_file in [int_file, float_file, byte_file, unsigned_int_file, string_file, percentage_file]:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(44100)
                
            # Convertir y escribir los datos en cada archivo
            int_file.writeframes(value.to_bytes(2, 'little'))
            float_file.writeframes(int(float(value)).to_bytes(2, 'little'))
            byte_file.writeframes(value.to_bytes(2, 'little'))
            unsigned_int_file.writeframes((value & 0xFFFF).to_bytes(2, 'little'))
            string_file.writeframes(int(string_value).to_bytes(2, 'little'))
            percentage_file.writeframes(int(percent_value * 1023 / 100).to_bytes(2, 'little'))
            
    except Exception as e:
        print(f"Error escribiendo archivos de audio: {e}")

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
    print(f"Creando archivos de audio para el archivo número: {file_number}")
    try:
        with open(log_file_path, 'a') as log_file:
            # Lee y escribe en los archivos durante 15 segundos
            end_time = start_time + 15
            while time.time() < end_time:
                value = read_channel(0)
                if value is not None:
                    # Registro del valor leído y sus interpretaciones
                    log_value(value, log_file)
                    
                    # Escribir datos en archivos de audio
                    write_audio_files(value, file_number)
                    
                    # Debug: Mostrar el valor leído
                    print(f"Valor leído: {value}")
                else:
                    print("No se recibió valor del canal SPI")
    except Exception as e:
        print(f"Error escribiendo el archivo de audio: {e}")
