import os
import sys
import aiohttp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import SERVER_URL


async def set_command(file_path, person, text):
    print("Enviando comando...", file_path, person, text)
    data = {'filename': os.path.basename(file_path), 'person': person, 'text': text}
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{SERVER_URL}/set-command', data=data) as response:
            if response.status == 200:
                print("Comando enviado correctamente:", await response.text())
            else:
                print("Error al enviar el comando:", await response.text())

async def finish_command():
    async with aiohttp.ClientSession() as session:
        print("Finalizando comando...")
        async with session.post(f'{SERVER_URL}/finish-command') as response:
            if response.status == 200:
                print("Comando finalizado correctamente")
            else:
                print("Error al finalizar el comando:", await response.text())

