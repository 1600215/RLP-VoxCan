import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def distancia():
    # Envía una señal de disparo de 10us
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Espera la recepción de la señal
    while GPIO.input(ECHO) == 0:
        pulso_inicio = time.time()

    while GPIO.input(ECHO) == 1:
        pulso_fin = time.time()

    # Calcula la duración del pulso y la distancia
    duracion_pulso = pulso_fin - pulso_inicio
    distancia = duracion_pulso * 17150
    distancia = round(distancia, 2)

    return distancia

try:
    while True:
        dist = distancia()
        print(f"Distancia: {dist} cm")
        time.sleep(1)
except KeyboardInterrupt:
    print("Medición detenida por el usuario")
    GPIO.cleanup()
