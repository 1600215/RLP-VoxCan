import os
import time
import requests
import random

AUDIO_FOLDER = './uploads'  # Cambia esto por la ruta de tu carpeta de destino
SERVER = 'http://localhost:3000'


def predict(audio):
    # Genera un número aleatorio entre 0 y 1
    r = random.random()
    if r < 0.8:
        return 4
    else:
        # Retorna 0, 1, 2 o 3 con igual probabilidad (0.05 cada uno)
        return random.choice([0, 1, 2, 3])

print("Esperando comando desde la Raspberry Pi...")

while True:
    archivos = os.listdir(AUDIO_FOLDER)
    
    for archivo in archivos:
        if archivo.lower().endswith('.mp3'):
            print(f"Nuevo archivo MP3 detectado: {archivo}")
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            
            try: 
                res = predict(audio=ruta_archivo)
                if res != 4:
                    print("Comando predicho:", res)
                    try:
                        response = requests.post(SERVER + '/set-command', json={'filename': archivo})
                        if response.status_code == 200:
                            print(f"Nombre de archivo '{archivo}' enviado al servidor correctamente.")
                        else:
                            print(f"Error al enviar el nombre de archivo '{archivo}' al servidor. Código de estado: {response.status_code}")                                
                    except Exception as e:
                        print(f"Error al enviar el nombre de archivo '{archivo}' al servidor o al eliminar el archivo: {e}")
                else:
                    print("Comando no reconocido.")
            except Exception as e:
                print("Error al predecir el comando de voz:", e)
            
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")

    time.sleep(1)
