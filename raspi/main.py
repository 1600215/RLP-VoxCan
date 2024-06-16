import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO
from constants import State, Axis, LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW, MPU6050_ADDR, AUDIO_FOLDER, INIT_IZQUIERDA_SUP, INIT_DERECHA_SUP, INIT_DERECHA_INF, INIT_IZQUIERDA_INF
from modules.arduino import connect
from modules.arduino import setPos
from modules.audio import process_files
from modules.calibrate import calibrate_servos
from modules.motion import calibrate_servo
from modules.web import finish_command

#para pruebas
from test.testStandby.test.testStandby import sit, standup, rotate, walk
import asyncio


#--------------------------------------------------------------
# Variables globales
current_state = State.INITIALIZE
rotate_degrees = None
standby_params = None
calibration = {}
ser = None
mpu = None
queueAudio = asyncio.Queue()
queueWalk = asyncio.Queue()
    

#--------------------------------------------------------------
# Inicialización de hardware
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

#--------------------------------------------------------------
# Función principal main VoxCan
async def main():
    
    #declarar variables globales
    global current_state, calibration, standby_params, rotate_degrees
        
    t = time.time()
    #----------------------------------------------------
    #Estados de la máquina de estado
    while True:
        try:
            #----------------------------------------------------
            #Estado CONNECT
            if current_state == State.CONNECT:
                """
                En el estado CONNECT, se intenta establecer una conexión con el Arduino Nano
                a través del puerto serie. Si la conexión se establece correctamente, se realiza
                un juego de luces y se cambia al estado SET_INIT.
                """
                
                # Si la conexión con el Arduino Nano está abierta
                if ser.isOpen():
                    time.sleep(1)  # Esperar a que el puerto serie se abra correctamente
                    try:
                        #intentar conectar
                        if connect(ser):
                            try:
                                #juego de luzes en caso de conectarse
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
                                
                                #cambio de estado a SET_INIT
                                current_state = State.SET_INIT
                                
                                #poner led YELLOW -> HIGH
                                GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)

                            #escpecion para los leds
                            except Exception as e:
                                raise Exception("Error al hacer juego de luces en el estado CONNECT", e)
                            
                        #10 segundos para conectarse con arduino
                        else:
                            if time.time() - t > 10:
                                raise Exception("Error al conectar con el Arduino Nano") 
                            
                    #escpeción para el comando connect
                    except Exception as e:
                        raise Exception("Error al enviar el comando de conexión al Arduino Nano", e)
                
                #10 segundos para abrir puerto serie sino ERROR
                elif time.time() - t > 10:
                    raise Exception("Error al abrir el puerto serie")
                
            #----------------------------------------------------
            # Estad SET_INIT
            elif current_state == State.SET_INIT:
                """
                En el estado SET_INIT, se envían comandos al Arduino para establecer
                las posiciones iniciales de los servos. Luego, se realiza un juego de luces
                y se cambia al estado CALIBRATION.
                """
                #mandar comando setPos a arduino con posiciones de inicialización
                if setPos(ser, mpu, {str(Axis.DERECHO_SUP): INIT_DERECHA_SUP, str(Axis.DERECHO_INF): INIT_DERECHA_INF, str(Axis.IZQUIERDO_SUP): INIT_IZQUIERDA_SUP, str(Axis.IZQUIERDO_INF): INIT_IZQUIERDA_INF}):
                    print("Posición inicial establecida")
                    
                    #juego de luces de color YELLOW para indicar que se ha inicializado
                    try:
                        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                        await asyncio.sleep(0.5)
                        GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                        await asyncio.sleep(0.5)
                        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                        await asyncio.sleep(0.5)
                        GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                        await asyncio.sleep(0.5)
                        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                        await asyncio.sleep(0.5)
                        GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                        
                    #excepción para el control de los LEDS
                    except Exception as e:
                        raise Exception("Error al poner el pin GPIO del led amarillo en alto en el estado SET_INIT", e)
                    
                    #cambiar de estado a CALIBRATION
                    current_state = State.CALIBRATION
                    
                #excpeción para comando setPos
                else:
                    raise Exception("Error al enviar los parámetros de la posición inicial")
                
            #-----------------------------------------------------------------------    
            #Estado CALIBRATION      
            elif current_state == State.CALIBRATION:
                """
                En el estado CALIBRATION, se calibra el servomotor utilizando el MPU6050.
                Luego, se configuran los parámetros de calibración y se cambia al estado STANDBY.
                """
                #calibrar los servos,  devuelve posiciones optimas de desbalance
                standby_params = calibrate_servos(ser, mpu)
                if standby_params == None: 
                    raise Exception("Error al calibrar los servos")

                #posicionar el robot en esa configuración
                set = setPos(ser, standby_params)
                if not set:
                    raise Exception("Error al enviar los parámetros de calibración, durante estado calibración")
                
                #configurar diccionario de calibración para poder relacionar cinematica directa/inversa con posiciones de los servos
                calibration = calibrate_servo(Axis.DERECHO_SUP, 175, standby_params[Axis.DERECHO_SUP], calibration)
                calibration = calibrate_servo(Axis.DERECHO_INF, 100, standby_params[Axis.DERECHO_INF], calibration)
                calibration = calibrate_servo(Axis.IZQUIERDO_SUP, 175, standby_params[Axis.IZQUIERDO_SUP], calibration)
                calibration = calibrate_servo(Axis.IZQUIERDO_INF, 100, standby_params[Axis.IZQUIERDO_INF], calibration)
                
                #try -> catch para poner GREEN en HIGH y YELLOW en LOW
                try:
                    GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
                    GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                
                #excepción por el control de los LEDS
                except Exception as e:
                    raise Exception("Error al poner el pin GPIO del led verde en alto y el amarillo en bajo en el estado CALIBRATION", e)
                
                
                #cambio de estado a estado STANDBY
                current_state = State.STANDBY
                
            #-----------------------------------------------------------------------    
            #Estado STANDBY
            elif current_state == State.STANDBY:
                
                """
                En el estado STANDBY, el sistema espera nuevos comandos
                """   
                             
                while True: 
                    print(f"Estado actual STANDBY, esperando nuevos comandos")
                    
                    # Llamar a process_files con la variable global current_state
                    audio_task = asyncio.create_task(process_files( audio_folder=AUDIO_FOLDER, state=current_state))
                    
                    # Esperar a que la tarea de procesamiento de audio se complete
                    next_state = await audio_task

                    #si devuevle un tupla -> estado siguiente ROTATE, inicializa variable rotate_degrees
                    #y también cambia de estado
                    if isinstance(next_state, tuple):
                        next, rotate_degrees = next_state
                        if next != current_state:
                            current_state = next
                            break
                    
                    #caso contrario cambia de estado a next_state
                    else:
                        if next_state != current_state:
                            current_state = next_state
                            print(f"Siguiente estado: {current_state}")
                            break

                await asyncio.sleep(1)
                
            #-----------------------------------------------------------------------    
            #Estado SIT
            elif current_state == State.SIT:

                """
                realizar comando SIT, genera la tarea y cuando termina manda finish_command al servidor,
                este volverá a habilitar el botón
                """
                
                #realizar comando sit con una tarea
                print("empezando estado SIT")
                sit_task = asyncio.create_task(sit())
                await sit_task
                
                #una vez terminado el comando SIT, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado SIT")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"Estado actual SIT, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    audio_task = asyncio.create_task(process_files( audio_folder=AUDIO_FOLDER, state=current_state))
                
                    # Esperar a que la tarea de procesamiento de audio se complete
                    next_state = await audio_task
                    
                    #en caso de cambiar de estado
                    if next_state != current_state:
                        current_state = next_state
                        print("Siguiente estado: ", current_state)               
                        break
                    
                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado STANDUP
            elif current_state == State.STANDUP:
                
                """
                realizar comando STANDUP, genera la tarea y cuando termina manda finish_command al servidor,
                este volverá a habilitar el botón
                """
                
                #realizar comando STANDUP con una tarea
                print("empezando estado STANDUP")
                sit_task = asyncio.create_task(standup())
                await sit_task
                
                #una vez terminado el comando STANDUP, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado STANDUP")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"Estado actual STANDUP, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    audio_task = asyncio.create_task(process_files( audio_folder=AUDIO_FOLDER, state=current_state))
                
                    # Esperar a que la tarea de procesamiento de audio se complete
                    next_state = await audio_task
                    
                    #si devuevle un tupla -> estado siguiente ROTATE, inicializa variable rotate_degrees
                    #y también cambia de estado
                    if isinstance(next_state, tuple):
                        next, rotate_degrees = next_state
                        if next != current_state:
                            current_state = next
                            break
                    
                    #caso contrario cambia de estado a next_state
                    else:
                        if next_state != current_state:
                            current_state = next_state
                            print(f"Siguiente estado: {current_state}")
                            break

                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado WALK
            elif current_state == State.WALK:
                
                print("Empezando estado WALK")
                
                """
                realizar comando WALK, genera la taska y se comunican las dos tareas mediante una cola,
                si entra un archivo de cambio de estado notifica y para de caminar
                """

                #tarea paralela a la lectura de archivos para no parar de andar hasta recibir otro comando y/o chocarse
                asyncio.create_task(walk(queue=(queueWalk, queueAudio)))
                    
                while True: 
                    
                    print(f"Estado actual WALK, esperando nuevos comandos")

                    #tarea para analizar la carpeta AUDIO_FOLDER
                    audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state, queue=(queueAudio, queueWalk)))
                    next_state = await audio_task

                    #si devuevle un tupla -> estado siguiente ROTATE, inicializa variable rotate_degrees
                    #y también cambia de estado
                    if isinstance(next_state, tuple):
                        next, rotate_degrees = next_state
                        if next != current_state:
                            current_state = next
                            break
                    
                    #caso contrario cambia de estado a next_state
                    else:
                        if next_state != current_state:
                            current_state = next_state
                            print(f"Siguiente estado: {current_state}")
                            break

                    await asyncio.sleep(1)
                   
            #-----------------------------------------------------------------------    
            #Estado ROTATE 
            elif current_state == State.ROTATE:
                """
                En el estado SIT_DOWN, el sistema ejecuta la acción de sentarse,
                utilizando la función sit. Luego, cambia de estado a STANDBY.
                """
                #realizar comando ROTATE
                print("empezando estado ROTATE")
                rotate_task = asyncio.create_task(rotate(rotate_degrees))
                await rotate_task
                
                #indicar a los usuarios de la web que se ha terminado el comando ROTATE
                print("terminado ROTATE")
                res = await finish_command()
                if not res: raise Exception("error")

                while True:
                    
                    print(f"Estado actual SIT, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    audio_task = asyncio.create_task(process_files( audio_folder=AUDIO_FOLDER, state=current_state))
                
                    # Esperar a que la tarea de procesamiento de audio se complete
                    next_state = await audio_task
                    
                    #en caso de cambiar de estado
                    if next_state != current_state:
                        current_state = next_state
                        print("Siguiente estado: ", current_state)               
                        break
                                        
                    await asyncio.sleep(1)
                    
            #estado no reconocido 
            else:
                raise Exception("Error estado no reconocido")
            
        # Excepción genérica
        except Exception as e:
            print(f"Error en la máquina de estados: {e}")
            GPIO.cleanup() #limpiar GPIO
            ser.close() #cerrar puerto serial
            sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupción por teclado, limpiando GPIO y cerrando puerto serie.")
        GPIO.cleanup()
        ser.close()