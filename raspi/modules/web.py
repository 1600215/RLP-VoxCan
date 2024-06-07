import os
import aiohttp
import ssl, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import SERVER

context = ssl.create_default_context()

context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

async def set_command(file_path, person, text):
    data = {'filename': os.path.basename(file_path), 'person': person, 'text': text}
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{SERVER}/set-command', data=data, ssl=context) as response:
            if response.status == 200:
                print("Comando enviado correctamente:", await response.text())
                return True
            else:
                print("Error al enviar el comando:", await response.text())
                return False

async def finish_command():
    async with aiohttp.ClientSession() as session:
        print("Finalizando comando...")
        async with session.post(f'{SERVER}/finish-command', ssl=context) as response:
            if response.status == 200:
                print("Comando finalizado correctamente")
                return True
            else:
                print("Error al finalizar el comando:", await response.text())
                return False
