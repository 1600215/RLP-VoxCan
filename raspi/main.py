import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO
from constants import Comºmand, Status, State, Axis, LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW, MPU6050_ADDR
from modules.connect import connect, AUDIO_FOLDER, SERVER
from modules.positions import getPos, setPos, calibrate_servos
from modules.accel import calcular_desbalanceo
import speech_recognition as sr
import joblib
import os
from voiceIdent import predict
import requests




#-----------------------------------------------------------------------
#Variables globales

current_state = State.INITIALIZE
standby_params = None
recognizer = sr.Recognizer()
modelo = joblib.load('modelo_preentrenado.pkl')

#-----------------------------------------------------------------------
#Inicialización de los pines GPIO de los leds 

try: 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN_GREEN, GPIO.OUT) # LED1
    GPIO.setup(18, GPIO.OUT)  # LED2
    GPIO.setup(24, GPIO.OUT)  # LED3
    
    try: 
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
    except Exception as e: 
        print("Error al poner los pines GPIO de los leds VERDE Y AMARILLO en bajo y ROJO eb alto en la fase inicia", e)
        sys.exit(1)
        
except Exception as e: 
    print("Error al inicializar los pines GPIO de los leds", e)
    sys.exit(1)


#-----------------------------------------------------------------------
# Inicialización del puerto serie y del mpu6050

try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

except Exception as e:
    print("Error de comunicación serial con Arduino Nano:", e)
    sys.exit(1)

#-----------------------------------------------------------------------
#Inicialización del MPU6050

try:
    mpu = mpu6050.mpu6050(MPU6050_ADDR)
    
except Exception as e:
    print("Error al inicializar el MPU6050:", e)
    sys.exit(1)
    

#-----------------------------------------------------------------------
#Bucle principal de la Raspberry Pi

t = time.time()

while True:

    try:
 
        #-----------------------------------------------------------------------
        #Estado inicial para realizar conexión con el arduino nano

        if current_state == State.CONNECT:
            #si la conexión con el Arduino Nano está abierta
            if ser.isOpen():
                
                print("Arduino Nano conectado")

                time.sleep(1) # Esperar a que el puerto serie se abra correctamente
                
                # Enviar el comazndo de conexión al Arduino 
                try:
                    if connect(ser):
                        
                        try:
                            GPIO.output(LED_PIN_RED, GPIO.HIGH)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_RED, GPIO.LOW)
                            GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_GREEN, GPIO.LOW)
                            GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                            time.sleep(0.5)
                            GPIO.output(LED_PIN_YELLOW, GPIO.LOW)

                            print("Conectado con arduino")
                        except Exception as e:
                            print("Error al poner el pin GPIO del led amarillo en alto en estado conect", e)
                            sys.exit(1)

                        current_state = State.SET_INIT
                    else:
                        print("Error al conectar con el Arduino Nano")
                        if time.time() - t > 10:
                            print("Error al conectar con el Arduino Nano")
                            break
                        
                except Exception as e:
                    print("Error al comunicarse con Arduino nano:", e)
                    break
            

        #-----------------------------------------------------------------------
        #Estado de calibración de los servos
        #Se utiiliza el led amarillo para indicar que se está calibrando los servos
        
        elif current_state == State.SET_INIT:            
            try:
                GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                
                if setPos(ser,mpu,  {str(Axis.DERECHO_SUP) : 135, str(Axis.DERECHO_INF) : 45, str(Axis.IZQUIERDO_SUP) : 100, str(Axis.IZQUIERDO_INF) : 100}):
                    print("Posición inicial establecida")
                
                else: 
                    print("Error al establecer la posición inicial")
                    sys.exit(1)
                
                
                GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                current_state = State.CALIBRATION

            except Exception as e:
                print("Error al poner el pin GPIO del led amarillo en bajo y el rojo en alto", e)
                sys.exit(1)
            
        
        elif current_state == State.CALIBRATION:  
            try: 
                GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                print("Calibrando servos...")

            except Exception as e:
                print("Error al poner el pin GPIO del led verde en bajo y el amarillo en alto", e)
                sys.exit(1)
            
            standby_params = calibrate_servos(ser, mpu)
            
            if standby_params is None:
                print("Error al calibrar los servos")
                sys.exit(1)
            
            print("Calibración finalizada")
            print("Parámetros de calibración:", standby_params)
            
            _, _ = setPos(ser, standby_params)

            try:
                
                GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                
            except Exception as e:
                print("Error al poner el pin GPIO del led verde en alto y el rojo en bajo", e)
                sys.exit(1)
            
            current_state = State.STANDBY
            
        #-----------------------------------------------------------------------    
        elif current_state == State.STANDBY:
            print("Esperando comando desde la Raspberry Pi...")


            # Obtener la lista de archivos en la carpeta
            archivos = os.listdir(AUDIO_FOLDER)
            
            # Verificar si hay nuevos archivos MP3
            for archivo in archivos:
                if archivo.lower().endswith('.mp3'):
                    print(f"Nuevo archivo MP3 detectado: {archivo}")
                    ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
                    
                    try: 
                        
                        res  = predict(audio=ruta_archivo)
                        if res != 4:
                            print("Persona predecida:", res)
                        
                            with sr.AudioFile(ruta_archivo) as source:
                                # Escuchar el archivo de audio
                                audio_data = recognizer.record(source)
                                # Reconocer el audio (usando el servicio de reconocimiento de Google)
                                try:
                                    text = recognizer.recognize_google(audio_data, language='es-ES')
                                    print("Texto reconocido:")
                                    print(text)
                                    if "sientate" in text:
                                        current_state = State.SIT
                                    elif "ven" in text:
                                        current_state = State.COME
                                except sr.UnknownValueError:
                                    print("Google Speech Recognition no pudo entender el audio")
                                except sr.RequestError as e:
                                    print(f"No se pudo solicitar resultados de Google Speech Recognition; {e}")
                            
                            try:
                                #no hace falta que la llamada sea asíncrona
                                response = requests.post(SERVER + '/set-command', json={'filename': archivo})
                                if response.status_code == 200:
                                    print(f"Nombre de archivo '{archivo}' enviado al servidor correctamente.")
                                else:
                                    print(f"Error al enviar el nombre de archivo '{archivo}' al servidor. Código de estado: {response.status_code}")                                
                            except Exception as e:
                                print(f"Error al enviar el nombre de archivo '{archivo}' al servidor o al eliminar el archivo: {e}")

                    except Exception as e:
                        print("Error al predecir el comando de voz:", e)
                    
                    try:
                        os.remove(ruta_archivo)
                        print(f"Archivo {archivo} eliminado correctamente.")
                    except Exception as e:
                        print(f"Error al eliminar el archivo {archivo}: {e}")

            time.sleep(1)

        #-----------------------------------------------------------------------
        elif current_state == State.SIT:
            try:
                GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                                
            except Exception as e:
                print("Error al poner el pin GPIO del led verde en alto", e)
                sys.exit(1)
            current_state = State.STANDBY
        
        #-----------------------------------------------------------------------
        elif current_state == State.COME:
            try:
                GPIO.output(LED_PIN_RED, GPIO.HIGH)
                                
            except Exception as e:
                print("Error al poner el pin GPIO del led rojo en alto", e)
                sys.exit(1)
            current_state = State.STANDBY

        #-----------------------------------------------------------------------
        else:
            print("Error")

    except Exception as e:
        print("Error en el bucle funcional:", e)
        break
