import os
import sys
import time
import asyncio


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.web import finish_command
from modules.audio import process_files
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
            await cleanup_files()   
            
        elif current_state == State.COME:
            print("Procesando comando COME...")
            time.sleep(20)
            await finish_command()
            current_state = State.STANDBY
            await cleanup_files()
        else: 
            print("Estado desconocido")
            break

async def cleanup_files():
    """
    Remove all files in the AUDIO_FOLDER directory.

    This function iterates over all files in the AUDIO_FOLDER directory and removes them one by one.
    If a file cannot be removed, an error message is printed.

    Parameters:
        None

    Returns:
        None
    """
    archivos = os.listdir(AUDIO_FOLDER)
    for archivo in archivos:
        ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
        try:
            os.remove(ruta_archivo)
            print(f"Archivo {archivo} eliminado correctamente.")
        except Exception as e:
            print(f"Error al eliminar el archivo {archivo}: {e}")

asyncio.run(main())
