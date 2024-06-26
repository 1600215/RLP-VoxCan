import serial
import time
import sys
import numpy as np
import RPi.GPIO as GPIO
from constants import State, LED_PIN_GREEN, LED_PIN_RED, LED_PIN_YELLOW, AUDIO_FOLDER, TRIG, ECHO
from modules.arduino import connect
from modules.audio import process_files
from modules.web import finish_command
from modules.motion import sit, standup, rotate, move_robot_with_imbalance
import asyncio

#--------------------------------------------------------------
# Variables globales
current_state = State.CONNECT
rotate_degrees = None
standby_params = None

ser = None
mpu = None

queueAudio = asyncio.Queue()
queueWalk = asyncio.Queue()
    

#--------------------------------------------------------------
# Inicialización de hardware


try:
    GPIO.setwarnings(False)
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
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

except  Exception as e:
    raise Exception("Error al inicializar los pines GPIO del sensor de ultrasonido", e)

#--------------------------------------------------------------
# Función principal main VoxCan
async def main():
    
    #declarar variables globales
    global current_state, standby_params, rotate_degrees
        
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
                
                print("ESTADO CONNECT")
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
                print("ESTADO SET_INIT")
       
                if not await standup(ser):
                    raise Exception("Error al enviar el comando de INIT-STANDUP al Arduino Nano")
                
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
                current_state = State.STANDBY
                
              
            #Estado STANDBY
            elif current_state == State.STANDBY:
                
                """
                En el estado STANDBY, el sistema espera nuevos comandos
                """   
                if not await rotate(ser, 0):
                    raise Exception("Error al realizar el comando de ROTATE")
                await asyncio.sleep(1)
                        
                while True: 
                    print(f"ESTADO STANDBY, esperando nuevos comandos")
                    
                    # Llamar a process_files con la variable global current_state
                    next_state = await process_files( audio_folder=AUDIO_FOLDER, state=current_state)
                    
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
                            break

                    await asyncio.sleep(1)
                
            #-----------------------------------------------------------------------    
            #Estado SIT
            elif current_state == State.SIT:

                """
                realizar comando SIT, genera la tarea y cuando termina manda finish_command al servidor,
                este volverá a habilitar el botón
                """
                print("ESTADO SIT")
                
                #realizar comando sit con una tarea
                print("empezando estado SIT")
                if not await sit(ser):
                    raise Exception("Error al realizer el comando de SIT")
                
                #una vez terminado el comando SIT, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado SIT")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"ESTADO SIT, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    next_state = await process_files( audio_folder=AUDIO_FOLDER, state=current_state)
                                    
                    #en caso de cambiar de estado
                    if next_state != current_state:
                        current_state = next_state
                        break
                    
                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado STANDUP
            elif current_state == State.STANDUP:
                
                """
                realizar comando STANDUP, genera la tarea y cuando termina manda finish_command al servidor,
                este volverá a habilitar el botón
                """
                
                print("ESTADO STANDUP")

                #realizar comando STANDUP con una tarea
                print("empezando estado STANDUP")
                if not await standup(ser):
                    raise Exception("Error al realizer el comando de STANDUP")
                
                #una vez terminado el comando STANDUP, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado STANDUP")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"ESTADO STANDUP, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    next_state = await process_files( audio_folder=AUDIO_FOLDER, state=current_state)
                    
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
                            break

                    await asyncio.sleep(1)
            
            #-----------------------------------------------------------------------    
            #Estado WALK
            elif current_state == State.WALK:
                
                print("ESTADO WALK")
                
                """
                realizar comando WALK, genera la taska y se comunican las dos tareas mediante una cola,
                si entra un archivo de cambio de estado notifica y para de caminar
                """

                #tarea paralela a la lectura de archivos para no parar de andar hasta recibir otro comando y/o chocarse
                asyncio.create_task(move_robot_with_imbalance(ser, queue=(queueWalk, queueAudio)))
                    
                while True: 
                    
                    print(f"ESTADO WALK, esperando nuevos comandos")

                    #tarea para analizar la carpeta AUDIO_FOLDER
                    next_state = await process_files(audio_folder=AUDIO_FOLDER, state=current_state, queue=(queueAudio, queueWalk))

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
                            break

                    await asyncio.sleep(1)
                   
            #-----------------------------------------------------------------------    
            #Estado ROTATE 
            elif current_state == State.ROTATE:
                """
                En el estado SIT_DOWN, el sistema ejecuta la acción de sentarse,
                utilizando la función sit. Luego, cambia de estado a STANDBY.
                """
                print("ESTADO ROTATE")
                #realizar comando ROTATE
                print("empezando estado ROTATE")
                if not await rotate(ser, rotate_degrees):
                    raise Exception("Error al realizar el comando de ROTATE")
                
                #indicar a los usuarios de la web que se ha terminado el comando ROTATE
                print("terminado ROTATE")
                res = await finish_command()
                if not res: raise Exception("error")

                while True:
                    
                    print(f"ESTADO ROTATE, esperando nuevos comandos")
                    
                    #generar una tarea para analizar los archivos de AUDIO_FOLDER
                    next_state = await process_files( audio_folder=AUDIO_FOLDER, state=current_state)

                    #en caso de cambiar de estado
                    if next_state != current_state:
                        current_state = next_state
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