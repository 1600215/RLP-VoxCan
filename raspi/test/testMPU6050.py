import time
import mpu6050

def testMPU6050():
    # Inicializar el sensor MPU6050
    sensor = mpu6050(0x68)

    try:
        while True:
            # Leer datos del acelerómetro y giroscopio
            accel_data = sensor.get_accel_data()
            gyro_data = sensor.get_gyro_data()

            # Imprimir los datos
            print(f"Accel: X={accel_data['x']:.2f}, Y={accel_data['y']:.2f}, Z={accel_data['z']:.2f}")
            print(f"Gyro: X={gyro_data['x']:.2f}, Y={gyro_data['y']:.2f}, Z={gyro_data['z']:.2f}")
            
            # Esperar un segundo antes de la siguiente lectura
            time.sleep(1)

    except KeyboardInterrupt:
        # Interrupción por teclado (Ctrl+C)
        print("\nInterrupción por teclado")
    except Exception as e:
        # Otras interrupciones
        print(f"Otra interrupción: {e}")

# Llamar a la función testLeds para ejecutar la prueba
testMPU6050()
