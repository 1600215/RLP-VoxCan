
import sys, os
from pydub import AudioSegment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from voiceIdent import predict


AUDIO_FOLDER = 'audioTest'

def convertName(name):
    if name == 'Adria':
        return 3
    elif name == 'Albert':
        return 1
    elif name == 'Raul':
        return 2
    elif name == 'Gerard':
        return 0
    else:
        return 4
        
def testPredict():
    archivos = os.listdir(AUDIO_FOLDER)
    i = 0
    for archivo in archivos:
        if archivo.lower().endswith('.mp3'):
            print(f"Nuevo archivo mp3 detectado: {archivo}")
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            try:

                audio = AudioSegment.from_file(ruta_archivo)
                audio.export(ruta_archivo, format="wav")
                
                res, t = predict(audio=ruta_archivo)
                
            except Exception as e:
                print("Error al predecir persona:", e)
                break
            
            if res != convertName(archivo.split('_')[1]):
                print("Error en la predicción:", archivo.split('_')[1], res)
            else : 
                i = i + 1
                print("Persona reconocido correctamente:", archivo.split('_')[1], res)
            print("tiempo de ejecución:", t)

    print("Test passed con ", i, " de ", len(archivos), " archivos")

if __name__ == '__main__':
    testPredict()
