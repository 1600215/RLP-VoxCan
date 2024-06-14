import os
import sys
import asyncio

AUDIO_FOLDER = os.path.abspath('uploads')  # Cambia esto por la ruta de tu carpeta de destino

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.audio import process_files
from constants import State

current_state = State.STANDBY  # Variable global para el estado actual
rotate_degrees = None  # Variable global para los grados de giro

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
    while True:
        if current_state == State.STANDBY:
            #todo NADA
            while True: 
                print("Esperando comando desde la Raspberry Pi...")
                # Llamar a process_files con la variable global current_state
                audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                
                print(f"Current state: {current_state}")
        
                # Esperar a que la tarea de procesamiento de audio se complete
                next_state = await audio_task
                print(f"Audio processing completed. Next state: {next_state}")


                if isinstance(next_state, tuple):
                    current_state, rotate_degrees = next_state
                else:
                    current_state = next_state

                if next_state != current_state:
                    break

                await asyncio.sleep(1)

        elif current_state == State.SIT:
            
            #todo lo relacionado con el sentarse llamando a una tarea
            
            while True:
                audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                
                print(f"Current state: {current_state}")
            
        
                # Esperar a que la tarea de procesamiento de audio se complete
                next_state = await audio_task
                print(f"Audio processing completed. Next state: {next_state}")

                if next_state != current_state:
                    current_state = next_state
                    break
                
                await asyncio.sleep(1)
        
        elif current_state == State.STANDUP:
            
            #todo codigo relacionado con levantarse llamando a una tarea
            
            while True: 
                audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                
                print(f"Current state: {current_state}")
                # Esperar a que la tarea de procesamiento de audio se complete
                next_state = await audio_task
                print(f"Audio processing completed. Next state: {next_state}")

                if isinstance(next_state, tuple):
                    current_state, rotate_degrees = next_state
                else:
                    current_state = next_state

                if next_state != current_state:
                    break

                await asyncio.sleep(1)

    
        elif current_state == State.WALK:
            
            #todo lo relacionado con el movimiento llamando a una tarea
            
            while True: 
                audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                
                print(f"Current state: {current_state}")
                # Esperar a que la tarea de procesamiento de audio se complete
                next_state = await audio_task
                print(f"Audio processing completed. Next state: {next_state}")

                if isinstance(next_state, tuple):
                    current_state, rotate_degrees = next_state
                else:
                    current_state = next_state

                if next_state != current_state:
                    break
                
                await asyncio.sleep(1)
                
        elif current_state == State.ROTATE:
            
            #todo lo relacionado con el giro llamando a una tarea
            print("Grados de giro:", rotate_degrees)
            
            
            while True:
                audio_task = asyncio.create_task(process_files(audio_folder=AUDIO_FOLDER, state=current_state))
                
                print(f"Current state: {current_state}")
                # Esperar a que la tarea de procesamiento de audio se complete
                next_state = await audio_task
                print(f"Audio processing completed. Next state: {next_state}")

                if next_state != current_state:
                    current_state = next_state
                    break
                
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
