
import sys, os
import asyncio
from pydub import AudioSegment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.audio import recognize_audio

AUDIO_FOLDER = os.path.abspath('audioTest')  # Cambia esto por la ruta de tu carpeta de destino


async def testRecognizeAudio():
    """
    Test the audio recognition functionality.
    
    This function reads all the MP3 files in the specified audio folder, converts them to WAV format,
    and then performs audio recognition on each file using the `recognize_audio` function. The recognized
    text is printed to the console.
    
    Returns:
        None
    """
    archivos = os.listdir(AUDIO_FOLDER)
    for archivo in archivos:
        if archivo.lower().endswith('.mp3'):
            print(f"Nuevo archivo MP3 detectado: {archivo}")
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            try:
                audio = AudioSegment.from_file(ruta_archivo)
                audio.export(ruta_archivo, format="wav")
                
                res = await recognize_audio(ruta_archivo)
                print("Texto reconocido:", res)
                
            except Exception as e:
                print("Error al predecir el comando de voz:", e)
                
if __name__ == '__main__':
    asyncio.run(testRecognizeAudio())