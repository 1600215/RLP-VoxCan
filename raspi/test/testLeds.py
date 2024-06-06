import time
import RPi.GPIO as GPIO
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW
def testLeds():

    # Configurar los GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN_RED, GPIO.OUT)
    GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
    GPIO.setup(LED_PIN_YELLOW, GPIO.OUT)

    try:
        while True:
            # Encender LED rojo, apagar otros
            GPIO.output(LED_PIN_RED, GPIO.HIGH)
            GPIO.output(LED_PIN_GREEN, GPIO.LOW)
            GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
            time.sleep(1)

            # Encender LED verde, apagar otros
            GPIO.output(LED_PIN_RED, GPIO.LOW)
            GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
            GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
            time.sleep(1)

            # Encender LED azul, apagar otros
            GPIO.output(LED_PIN_RED, GPIO.LOW)
            GPIO.output(LED_PIN_GREEN, GPIO.LOW)
            GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
            time.sleep(1)

    except KeyboardInterrupt:
        # Interrupción por teclado (Ctrl+C)
        print("\nInterrupción por teclado")
    except Exception as e:
        # Otras interrupciones
        print(f"Otra interrupción: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO.cleanup() ejecutado")

# Llamar a la función testLeds para ejecutar la prueba
testLeds()
