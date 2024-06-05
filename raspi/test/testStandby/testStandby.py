import os
import sys
import time
import aiohttp
import asyncio
import random
import speech_recognition as sr
from pydub import AudioSegment
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from constants import State

AUDIO_FOLDER = '../../../webServer/uploads'  # Cambia esto por la ruta de tu carpeta de destino
SERVER_URL = 'http://localhost:3000'

async def predict(audio):
    await asyncio.sleep(4)
    r = random.random()
    if r < 0.2:
        return 4
    else:
        return random.choice([0, 1, 2, 3])

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

async def main():
    current_state = 'STANDBY'
    while True:
        if current_state == 'STANDBY':
            print("Esperando comando desde la Raspberry Pi...")
            ret = await process_files()
            if ret:
                current_state = 'PROCESSING'
            await asyncio.sleep(1)
        elif current_state == 'PROCESSING':
            print("Procesando comando...")
            time.sleep(20)
            await finish_command()
            current_state = 'STANDBY'
            await cleanup_files()   




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

asyncio.run(main())
