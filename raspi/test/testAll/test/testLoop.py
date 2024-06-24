import os
import sys
import asyncio

AUDIO_FOLDER = os.path.abspath('uploads')  # Cambia esto por la ruta de tu carpeta de destino

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.audio import process_files
from modules.web import finish_command
from constants import State, MESSAGE_WALK, MESSAGE_AUDIO

current_state = State.STANDBY  # Variable global para el estado actual
rotate_degrees = None  # Variable global para los grados de giro


async def sit():
    await asyncio.sleep(10)
    return 

async def rotate(degrees):
    print("ROTATE ", degrees)
    await asyncio.sleep(10)
    return 

async def standup():
    await asyncio.sleep(10)
    return

async def walk(queue):
    
    if not isinstance(queue, tuple):
        return 
    queueWalk, queueAudio = queue
    count = 0
    
    while True:
        print("moviendo pierna izquierda")
        #mover pierna izquierda
        await asyncio.sleep(1)
        #mover pierna derecha
        print("moviendo pierna derecha")
        await asyncio.sleep(1)
        
        #comprobar que robot no se choca mediante el sensor ultrasonidos
        if count > 5:
            print("Limite, se choca el robot")
            await queueWalk.put(MESSAGE_WALK)
            await asyncio.sleep(1)
            return
        #comprobar que robot no quiere cambiar de estado
        if not queueAudio.empty():
            incoming_message = await queueAudio.get()
            if incoming_message == MESSAGE_AUDIO :
                print("Cambio de estado recibido")
                return 
        count = count + 1

async def main():
    """
    Main function that controls the state transitions and audio processing.

    This function continuously checks the current state and performs the corresponding actions based on the state.
    It calls the `process_files` function to process audio files based on the current state.
    The function waits for the audio processing task to complete and updates the current state accordingly.
    If the next state is different from the current state, the loop breaks and transitions to the new state.
    The function also handles the rotation degrees when the state is `ROTATE`.

    Returns:
        None
    """
    global current_state, rotate_degrees
    queueAudio = asyncio.Queue()
    queueWalk = asyncio.Queue()
    
    while True:
                   #Estado STANDBY
        if current_state == State.STANDBY:
            
            """
            En el estado STANDBY, el sistema espera nuevos comandos
            """   
                            
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
            sit_task = await sit()
            
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
            sit_task = await standup()
            
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
            if not await rotate(rotate_degrees):
                raise Exception("error")
            
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
                    print("Siguiente estado: ", current_state)               
                    break
                                    
                await asyncio.sleep(1)
                
if __name__ == "__main__":
    asyncio.run(main())
