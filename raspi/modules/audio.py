
import speech_recognition as sr
from pydub import AudioSegment
import io
import sys, os

from modules.web import set_command


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import State, AUDIO_FOLDER
from voiceIdent import predict


async def recognize_audio(file_path):
    """
    Recognizes audio from a WAV file using the Google Speech Recognition API.

    Parameters:
    file_path (str): The path to the WAV file.

    Returns:
    str: The recognized text from the audio file.

    Raises:
    UnknownValueError: If Google Speech Recognition cannot understand the audio.
    RequestError: If there is an error requesting results from Google Speech Recognition.
    Exception: If there is an error processing the audio file.
    """
    recognizer = sr.Recognizer()
    
    try:
        # Use speech_recognition to recognize audio directly from the WAV file
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='es-ES')
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition; {e}")
                return None
    except Exception as e:
        print(f"Error processing the audio file: {e}")
        return None


async def recognize_audio_from_file(file_path):
    """
    Recognizes audio from a file and performs actions based on the recognized text.

    Parameters:
    file_path (str): The path to the audio file.

    Returns:
    str or None: The state of the action performed based on the recognized text. Possible values are 'State.SIT', 'State.COME', or None.
    """
    
    audio = AudioSegment.from_file(file_path)
    audio.export(file_path, format="wav")
    
    person, t = predict(audio=file_path)
    print("Persona identificada:", person, "en tiempo:", t)
    
    if person == 4:
        return None
    
    
    text = await recognize_audio(file_path)
    print("Texto reconocido:", text)
    
    if text is None:
        return None
    
    if "siéntate" in text:
        
        res = await set_command(file_path, person, text)
        
        if res: return State.SIT
        else: return None
                
    elif "ven aquí" in text:
        
        res = await set_command(file_path, person, text)
        
        if res: return State.COME
        else: return None
                
    else: return None
                


async def process_files(audio_folder=AUDIO_FOLDER):
    """
    Process audio files in the specified folder.

    Parameters:
    - audio_folder (str): Path to the folder containing audio files. Default is `AUDIO_FOLDER`.

    Returns:
    - res: The result of the audio processing.

    Raises:
    - Exception: If there is an error while predicting the voice command or deleting the file.
    """
    
    archivos = os.listdir(audio_folder)
    res = None
    for archivo in archivos:
        
        if archivo.lower().endswith('.wav'):
            
            print(f"Nuevo archivo WAV detectado: {archivo}")
            ruta_archivo = os.path.join(audio_folder, archivo)
            
            try:
                res = await recognize_audio_from_file(ruta_archivo)
                
            except Exception as e:
                print("Error al predecir el comando de voz:", e)
                
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")
    return res



async def cleanup_files():
    """
    Clean up audio files in the specified folder.

    This function removes all audio files with the '.wav' extension from the specified folder.

    Returns:
        None

    Raises:
        OSError: If there is an error while removing the file.

    """
    
    archivos = os.listdir(AUDIO_FOLDER)
    for archivo in archivos:
        if archivo.lower().endswith('.wav'):
            ruta_archivo = os.path.join(AUDIO_FOLDER, archivo)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")
