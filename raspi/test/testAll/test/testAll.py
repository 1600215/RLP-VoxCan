import serial
import time
import sys, os



AUDIO_FOLDER = os.path.abspath('uploads')  # Cambia esto por la ruta de tu carpeta de destino

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from constants import State
from modules.arduino import connect
from modules.audio import process_files
from modules.web import finish_command
from modules.motion import sit, standup, rotate, move_robot_with_imbalance

#para pruebas
import asyncio

#--------------------------------------------------------------
# Variables globales
current_state = State.CONNECT
rotate_degrees = None
ser = None
queueAudio = asyncio.Queue()
queueWalk = asyncio.Queue()
    
#--------------------------------------------------------------
# Inicialización de hardware

try:
    # Inicialización del puerto serie
    ser = serial.Serial(port='/dev/tty.usbserial-14130', baudrate=9600, timeout=1)
except serial.SerialException as se:
    raise Exception("Error al inicializar el puerto serie", se)


#--------------------------------------------------------------
# Función principal main VoxCan
async def main():
    
    #declarar variables globales
    global current_state, rotate_degrees
        
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

                            current_state = State.SET_INIT
                            print("Conexión establecida con el Arduino Nano")
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
                #mandar comandos de standup a arduino con posiciones de inicialización
                if await standup(ser):
                    print("Posiciones iniciales enviadas al Arduino Nano")
                else:
                    raise Exception("Error al enviar los parámetros de la posición inicial")
            
                current_state = State.STANDBY
                
              
            #Estado STANDBY
            elif current_state == State.STANDBY:
                
                """
                En el estado STANDBY, el sistema espera nuevos comandos
                """   
                
                if not await rotate(ser, 0):
                    raise Exception("Error al enviar el comando de rotación al Arduino Nano")
                
                while True: 
                    print(f"Estado actual STANDBY, esperando nuevos comandos")
                    
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
                
                #realizar comando sit con una tarea
                print("empezando estado SIT")
                if not await sit(ser):
                    raise Exception("Error al enviar el comando de sentarse al Arduino Nano")
                
                #una vez terminado el comando SIT, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado SIT")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"Estado actual SIT, esperando nuevos comandos")
                    
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
                
                #realizar comando STANDUP con una tarea
                print("empezando estado STANDUP")
                if not await standup(ser):
                    raise Exception("Error al enviar el comando de levantarse al Arduino Nano")
                
                #una vez terminado el comando STANDUP, comunicar que se finaliza el comando a los usarios de la web, sino se devuelve codigo 200 ERROR.
                print("terminado STANDUP")
                res = await finish_command()
                if not res: 
                    raise Exception("error")

                #bucle infinito para generar tareas que analizen la carpeta AUDIO_FOLDER
                while True:
                    
                    print(f"Estado actual STANDUP, esperando nuevos comandos")
                    
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
                
                """
                realizar comando WALK, genera la taska y se comunican las dos tareas mediante una cola,
                si entra un archivo de cambio de estado notifica y para de caminar
                """
                
                print("Empezando estado WALK")
                #tarea paralela a la lectura de archivos para no parar de andar hasta recibir otro comando y/o chocarse
                task_walk = asyncio.create_task(move_robot_with_imbalance(ser, queue=(queueWalk, queueAudio)))    
                    
                while True: 
    
                    print(f"Estado actual WALK, esperando nuevos comandos")

                    #tarea para analizar la carpeta AUDIO_FOLDER
                    next_state = await process_files( audio_folder=AUDIO_FOLDER, state=current_state, queue=(queueAudio, queueWalk))

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
                await task_walk
                 
            #-----------------------------------------------------------------------    
            #Estado ROTATE 
            elif current_state == State.ROTATE:
                """
                En el estado SIT_DOWN, el sistema ejecuta la acción de sentarse,
                utilizando la función sit. Luego, cambia de estado a STANDBY.
                """
                #realizar comando ROTATE
                print("empezando estado ROTATE")
                if not await rotate(ser, rotate_degrees):
                    raise Exception("Error al enviar el comando de rotación al Arduino Nano")

                
                #indicar a los usuarios de la web que se ha terminado el comando ROTATE
                print("terminado ROTATE")
                res = await finish_command()
                if not res: raise Exception("error")

                while True:
                    
                    print(f"Estado actual ROTATE, esperando nuevos comandos")
                    
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
            ser.close() #cerrar puerto serial
            sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupción por teclado, limpiando GPIO y cerrando puerto serie.")
        ser.close()