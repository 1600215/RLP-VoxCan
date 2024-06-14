import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO
from constants import State, Axis, LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW, MPU6050_ADDR, WALK, AUDIO_FOLDER
from modules.connect import connect
from modules.positions import setPos
from modules.audio import process_files
from modules.calibrate import calibrate_servos
from modules.motion import calibrate_servo
import asyncio

# Variables globales
current_state = State.INITIALIZE
rotate_degrees = None
standby_params = None
calibration = {}

async def initialize_hardware():
    global ser, mpu
    
    try:
        # Inicialización de los pines GPIO de los leds
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN_GREEN, GPIO.OUT) # LED1
        GPIO.setup(LED_PIN_RED, GPIO.OUT)  # LED2
        GPIO.setup(LED_PIN_YELLOW, GPIO.OUT)  # LED3
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
    except Exception as e:
        raise Exception("Error al inicializar los pines GPIO de los leds", e)

    try:
        # Inicialización del puerto serie
        ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
    except serial.SerialException as se:
        raise Exception("Error al inicializar el puerto serie", se)
    
    try:
        # Inicialización del MPU6050
        mpu = mpu6050.mpu6050(MPU6050_ADDR)
    except Exception as e:
        raise Exception("Error al inicializar el MPU6050", e)

async def main():
    global current_state, calibration, standby_params, rotate_degrees
    
    # Inicialización de hardware
    await initialize_hardware()
    
    t = time.time()
    
    while True:
        try:
            if current_state == State.CONNECT:
                # Si la conexión con el Arduino Nano está abierta
                if ser.isOpen():
                    time.sleep(1)  # Esperar a que el puerto serie se abra correctamente
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
                                    i = i + 1
                                print("Conectado con arduino")
                                current_state = State.SET_INIT
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
        
            elif current_state == State.SET_INIT:
                try:
                    if setPos(ser, mpu, {str(Axis.DERECHO_SUP): 150, str(Axis.DERECHO_INF): 30, str(Axis.IZQUIERDO_SUP): 30, str(Axis.IZQUIERDO_INF): 135}):
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
            #Estado STANDBY
            elif current_state == State.STANDBY:
                
                """
                llamar a la tarea que ejecuta STANDBY (NADA)
                """
                
                while True:
                    print("Esperando comando desde la Raspberry Pi...")
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                    print(f"Current state: {current_state}")
                    next_state = await audio_task
                    print(f"Audio processing completed. Next state: {next_state}")
                    if isinstance(next_state, tuple):
                        current_state, rotate_degrees = next_state
                    else:
                        current_state = next_state
                    if next_state != current_state:
                        break
                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado SIT
            elif current_state == State.SIT:
                """
                llamar a la tarea que ejecuta SIT
                """
                while True:
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                    print(f"Current state: {current_state}")
                    next_state = await audio_task
                    print(f"Audio processing completed. Next state: {next_state}")
                    if next_state != current_state:
                        current_state = next_state
                        break
                    await asyncio.sleep(1)

            
            #-----------------------------------------------------------------------    
            #Estado de STANDUP de comandos desde la Raspberry Pi
            elif current_state == State.STANDUP:
                """
                llamar a la tarea que ejecuta STANDUP
                """
                while True:
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                    print(f"Current state: {current_state}")
                    next_state = await audio_task
                    print(f"Audio processing completed. Next state: {next_state}")
                    if isinstance(next_state, tuple):
                        current_state, rotate_degrees = next_state
                    else:
                        current_state = next_state
                    if next_state != current_state:
                        break
                    await asyncio.sleep(1)

            #-----------------------------------------------------------------------    
            #Estado de WALK de comandos desde la Raspberry Pi
            elif current_state == State.WALK:
                """
                llamar a la tarea que ejecuta WALK
                """
                while True:
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                    print(f"Current state: {current_state}")
                    next_state = await audio_task
                    print(f"Audio processing completed. Next state: {next_state}")
                    if isinstance(next_state, tuple):
                        current_state, rotate_degrees = next_state
                    else:
                        current_state = next_state
                    if next_state != current_state:
                        break
                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado de ROTATE de comandos desde la Raspberry Pi
            elif current_state == State.ROTATE:
                print("Grados de giro:", rotate_degrees)
                """
                llamar a la tarea que ejecuta ROTATE
                """
                while True:
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                    print(f"Current state: {current_state}")
                    next_state = await audio_task
                    print(f"Audio processing completed. Next state: {next_state}")
                    if next_state != current_state:
                        current_state = next_state
                        break
                    await asyncio.sleep(1)
            else:
                print("Error")
        except Exception as e:
            raise Exception("Error en el bucle principal", e)

if __name__ == "__main__":
    asyncio.run(main())
