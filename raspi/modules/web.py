import requests
from modules.connect import connect, AUDIO_FOLDER, SERVER


def set_command(archivo):
    try:
        #no hace falta que la llamada sea asíncrona
        response = requests.post(SERVER + '/set-command', json={'filename': archivo})
        if response.status_code == 200:
            print(f"Nombre de archivo '{archivo}' enviado al servidor correctamente.")
        else:
            print(f"Error al enviar el nombre de archivo '{archivo}' al servidor. Código de estado: {response.status_code}")                                
    except Exception as e:
        print(f"Error al enviar el nombre de archivo '{archivo}' al servidor o al eliminar el archivo: {e}")