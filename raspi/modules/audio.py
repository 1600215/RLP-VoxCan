
import speech_recognition as sr
from pydub import AudioSegment
import io
import sys, os

from modules.web import set_command


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import State, AUDIO_FOLDER
from voiceIdent import predict


async def recognize_audio_from_file(file_path):
    recognizer = sr.Recognizer()

    person = await predict(audio=file_path)
    if person == 4:
        return None
    
    audio = AudioSegment.from_mp3(file_path)
    wav_data = io.BytesIO()
    audio.export(wav_data, format="wav")

    with io.BytesIO(wav_data.getvalue()) as wav_io:
        wav_io.seek(0)
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='es-ES')
                print("Texto reconocido:")
                print(text)
                
                if "siéntate" in text:
                    await set_command(file_path, await predict(audio=file_path), text)
                    return State.SIT
                
                elif "ven aquí" in text:
                    await set_command(file_path, await predict(audio=file_path), text)
                    return State.COME
                
                else: return None
                
            except sr.UnknownValueError:
                print("Google Speech Recognition no pudo entender el audio")
            except sr.RequestError as e:
                print(f"No se pudo solicitar resultados de Google Speech Recognition; {e}")


async def process_files():
    archivos = os.listdir(AUDIO_FOLDER)
    for archivo in archivos:
        if archivo.lower().endswith('.mp3'):
            print(f"Nuevo archivo MP3 detectado: {archivo}")
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            try:
                res =  await recognize_audio_from_file(ruta_archivo)
            except Exception as e:
                print("Error al predecir el comando de voz:", e)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
                return res
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")

    return None


async def cleanup_files():
    archivos = os.listdir(AUDIO_FOLDER)
    for archivo in archivos:
        if archivo.lower().endswith('.mp3'):
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")
