import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO
from constants import State, Axis, LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW, MPU6050_ADDR
from modules.connect import connect
from modules.positions import setPos
from modules.audio import process_files, cleanup_files
from modules.calibrate import calibrate_servos
from modules.web import finish_command
from modules.motion import calibrate_servo, bajar_cadera
import asyncio


#-----------------------------------------------------------------------
#Variables globales
current_state = State.INITIALIZE
standby_params = None

calibration = {}

#-----------------------------------------------------------------------
#Inicialización de los pines GPIO de los leds 
try: 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN_GREEN, GPIO.OUT) # LED1
    GPIO.setup(LED_PIN_RED, GPIO.OUT)  # LED2
    GPIO.setup(LED_PIN_YELLOW, GPIO.OUT)  # LED3
    try: 
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
    except Exception as e: 
        raise Exception("Error al poner los pines GPIO de los leds VERDE Y AMARILLO en bajo y ROJO eb alto en la fase inicia", e)
        
except Exception as e: 
    raise Exception("Error al inicializar los pines GPIO de los leds", e)

#-----------------------------------------------------------------------
# Inicialización del puerto serie y del mpu6050
try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
except Exception as e:
    raise Exception("Error al inicializar el puerto serie", e)

#-----------------------------------------------------------------------
#Inicialización del MPU6050
try:
    mpu = mpu6050.mpu6050(MPU6050_ADDR)
except Exception as e:
    raise Exception("Error al inicializar el MPU6050", e)
    
#-----------------------------------------------------------------------
#Bucle principal de la Raspberry Pi
async def main():
    t = time.time()
    while True:
        try:
            #-----------------------------------------------------------------------
            #Estado inicial para realizar conexión con el arduino nano
            if current_state == State.CONNECT:    
                #si la conexión con el Arduino Nano está abierta
                if ser.isOpen():
                    time.sleep(1) # Esperar a que el puerto serie se abra correctamente
                    try:
                        if connect(ser):    
                            try:
                                i = 0
                                while i < 3:
                                    GPIO.output(LED_PIN_RED, GPIO.HIGH)
                                    time.sleep(0.5)
                                    GPIO.output(LED_PIN_RED, GPIO.LOW)
                                    GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                                    time.sleep(0.5)
                                    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
                                    GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                                    time.sleep(0.5)
                                    GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                                    i = i +1
                                #cambio de estado y mensaje para recibir output
                                print("Conectado con arduino")
                                current_state = State.SET_INIT
                                #preparar output de leds
                                try: 
                                    GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                                except Exception as e:
                                    raise Exception("Error al poner el pin GPIO del led amarillo en alto en el estado CONNECT -> SET_INIT", e)

                            except Exception as e:
                                raise Exception("Error al hacer juego de luces en el estado CONNECT", e)
                        else:
                            print("Error al conectar con el Arduino Nano")
                            if time.time() - t > 10:
                                raise Exception("Error al conectar con el Arduino Nano") 
                    except Exception as e:
                        raise Exception("Error al enviar el comando de conexión al Arduino Nano", e)
                elif time.time() - t > 10:
                    raise Exception("Error al abrir el puerto serie")
        
            #-----------------------------------------------------------------------
            #Estado de inicialización de las posiciones de los servos
            elif current_state == State.SET_INIT:            
                try:
                    if setPos(ser,mpu,  {str(Axis.DERECHO_SUP) : 150, str(Axis.DERECHO_INF) : 30, str(Axis.IZQUIERDO_SUP) : 30, str(Axis.IZQUIERDO_INF) : 135}):
                        print("Posición inicial establecida")
                        try: 
                            GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                        except Exception as e:
                            raise Exception("Error al poner el pin GPIO del led amarillo en alto en el estado SET_INIT", e)
                        current_state = State.CALIBRATION
                    else: 
                        raise Exception("Error al enviar los parámetros de la posición inicial")
                except Exception as e:
                    raise Exception("Error al enviar los parámetros de la posición inicial", e)

            #-----------------------------------------------------------------------    
            #Estado de calibración de los servos            
            elif current_state == State.CALIBRATION:  
                try:
                    standby_params = calibrate_servos(ser, mpu)
                    if standby_params is None:
                        raise Exception("Error al calibrar los servos")
                    set = setPos(ser, standby_params)
                    if not set: 
                        raise Exception("Error al enviar los parámetros de calibración, durante estado calibración")
                    calibration = calibrate_servo(Axis.DERECHO_SUP, 175, standby_params[Axis.DERECHO_SUP], calibration)
                    calibration = calibrate_servo(Axis.DERECHO_INF, 100, standby_params[Axis.DERECHO_INF], calibration)
                    calibration = calibrate_servo(Axis.IZQUIERDO_SUP, 175, standby_params[Axis.IZQUIERDO_SUP], calibration)
                    calibration = calibrate_servo(Axis.IZQUIERDO_INF, 100, standby_params[Axis.IZQUIERDO_INF], calibration)
                    try: 
                        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                        GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                    except Exception as e:
                        raise Exception("Error al poner el pin GPIO del led verde en alto y el amarillo en bajo en el estado CALIBRATION", e)
                    current_state = State.STANDBY
                except Exception as e:
                    raise Exception("Error al calibrar los servos, estado CALIBRACIÓN", e)
        
            #-----------------------------------------------------------------------    
            #Estado de STANDBY de comandos desde la Raspberry Pi
            elif current_state == State.STANDBY:
                print("Esperando comando desde la Raspberry Pi...")
                try:
                    ret = await process_files()
                    if ret != None:
                        try: 
                            GPIO.output(LED_PIN_GREEN, GPIO.LOW)
                            GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                        except Exception as e:
                            raise Exception("Error al poner el pin GPIO del led verde en bajo y el amarillo en alto en el estado STANDBY", e)
                        current_state = ret
                    await asyncio.sleep(1)
                except Exception as e:
                    raise Exception("Error al procesar los archivos de audio", e)
                    
            #-----------------------------------------------------------------------
            #Estado de SIT
            elif current_state == State.SIT:
                """
                comando SIT
                """
                await finish_command()
                await cleanup_files() 
                
                current_state = State.STANDBY
            
            #-----------------------------------------------------------------------
            elif current_state == State.COME:
                """
                comando COME
                """  
                await finish_command()
                await cleanup_files() 
                
                current_state = State.STANDBY

            #-----------------------------------------------------------------------
            else:
                print("Error")

        except Exception as e:
            raise Exception("Error en el bucle principal", e)

asyncio.run(main())
