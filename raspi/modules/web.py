import os
import aiohttp
import ssl, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import SERVER

context = ssl.create_default_context()

context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

async def set_command(file_path, person, text, command):
    """
    Sends a command to the server.

    Parameters:
    - file_path (str): The path of the file.
    - person (str): The person associated with the command.
    - text (str): The text of the command.

    Returns:
    - bool: True if the command was sent successfully, False otherwise.
    """
    data = {'filename': os.path.basename(file_path), 'person': person, 'text': text, 'command': command}
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{SERVER}/set-command', data=data, ssl=context) as response:
            if response.status == 200:
                print("Comando enviado correctamente:", await response.text())
                return True
            else:
                print("Error al enviar el comando:", await response.text())
                return False

async def go_standby():
    """
    Finish the command by sending a POST request to the server.

    Returns:
        bool: True if the command was finished successfully, False otherwise.
    """
    async with aiohttp.ClientSession() as session:
        print("Finalizando comando...")
        async with session.post(f'{SERVER}/go-standby', ssl=context) as response:
            if response.status == 200:
                print("Comando finalizado correctamente")
                return True
            else:
                print("Error al finalizar el comando:", await response.text())
                return False


async def finish_command():
    """
    Finish the command by sending a POST request to the server.

    Returns:
        bool: True if the command was finished successfully, False otherwise.
    """
    async with aiohttp.ClientSession() as session:
        print("Finalizando comando...")
        async with session.post(f'{SERVER}/finish-command', ssl=context) as response:
            if response.status == 200:
                print("Comando finalizado correctamente")
                return True
            else:
                print("Error al finalizar el comando:", await response.text())
                return False
