
import sys, os
from pydub import AudioSegment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from voiceIdent import predict


AUDIO_FOLDER = 'audioTest'

def convertName(name):
    """
    Convert a given name to a corresponding numerical value.

    Parameters:
    name (str): The name to be converted.

    Returns:
    int: The numerical value corresponding to the given name.
    """
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
    """
    Test the predict function on a list of audio files.

    This function iterates through the files in the AUDIO_FOLDER directory and performs the following steps for each file:
    1. Check if the file has a .mp3 extension.
    2. Convert the file to .wav format using the AudioSegment library.
    3. Call the predict function to predict the person in the audio.
    4. Compare the predicted result with the expected result.
    5. Print the result and execution time.

    If the predicted result matches the expected result, the function increments the counter variable i.

    At the end of the function, it prints the number of files passed and the total number of files.

    Returns:
    None
    """
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
            else:
                i = i + 1
                print("Persona reconocido correctamente:", archivo.split('_')[1], res)
            print("tiempo de ejecución:", t)
    print("Test passed con ", i, " de ", len(archivos), " archivos")

if __name__ == '__main__':
    testPredict()
