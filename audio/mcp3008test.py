import spidev
import time

# Inicializar SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus SPI 0, dispositivo CS 0
spi.max_speed_hz = 1350000  # Velocidad máxima del bus SPI

# Función para leer un canal del MCP3008
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def main():
    count = 0
    print("MCP3008 simple test.")

    while True:
        for chan in range(8):
            value = read_channel(chan)
            print(f"{value}\t", end="")
        print(f"[{count}]")
        count += 1
        time.sleep(1)

if __name__ == "__main__":
    main()
