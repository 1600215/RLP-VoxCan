import os
import sys
import time
import asyncio


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.web import finish_command
from modules.audio import process_files,cleanup_files
from constants import State

AUDIO_FOLDER = 'uploads'  # Cambia esto por la ruta de tu carpeta de destino


async def main():
    """
    Main function that controls the state transitions and commands.

    Returns:
        None
    """
    current_state = State.STANDBY
    while True:
        if current_state == State.STANDBY:
            print("Esperando comando desde la Raspberry Pi...")
            ret = await process_files(audio_folder=AUDIO_FOLDER)
            if ret:
                current_state = ret
            await asyncio.sleep(1)
            
        elif current_state == State.SIT:
            print("Procesando comando SIT...")
            time.sleep(20)
            await finish_command()
            current_state = State.STANDBY
            await cleanup_files(audio_folder=AUDIO_FOLDER)   
            
        elif current_state == State.COME:
            print("Procesando comando COME...")
            time.sleep(20)
            await finish_command()
            current_state = State.STANDBY
            await cleanup_files(audio_folder=AUDIO_FOLDER)
        else: 
            print("Estado desconocido")
            break


asyncio.run(main())
