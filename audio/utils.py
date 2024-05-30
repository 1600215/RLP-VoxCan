import spidev
import time



    # Configuración SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Abre el bus SPI 0, dispositivo (CS) 0
spi.max_speed_hz = 1350000  # Ajusta la velocidad del reloj SPI si es necesario

def read_adc(channel, spi):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def estimate_sample_rate(duration=5):
    """Estima el sample rate capturando datos del MCP3008 durante una duración especificada.

    Args:
        duration (int): Duración en segundos para capturar datos (predeterminado es 5 segundos).

    Returns:
        float: Sample rate estimado en Hz.
    """
    # Captura una pequeña cantidad de muestras para estimar el tiempo de una lectura
    num_initial_samples = 1000
    start_time = time.time()
    for _ in range(num_initial_samples):
        read_adc(0)
    end_time = time.time()
    
    # Calcula el tiempo promedio de una lectura
    elapsed_time = end_time - start_time
    avg_time_per_sample = elapsed_time / num_initial_samples
    
    # Calcula el número total de muestras para la duración deseada
    num_samples = int(duration / avg_time_per_sample)
    
    # Captura los datos para la duración especificada
    start_time = time.time()
    for _ in range(num_samples):
        read_adc(0)
    end_time = time.time()
    
    # Calcula el sample rate
    elapsed_time = end_time - start_time
    estimated_sample_rate = num_samples / elapsed_time
    
    return estimated_sample_rate


if __name__ == "__main__":
    

    print("Estimación del sample rate del MCP3008...")
    sample_rate = estimate_sample_rate()
    print(f"Sample rate estimado: {sample_rate} Hz")

    # Cierra la conexión SPI
    spi.close()
    
