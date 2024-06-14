import speech_recognition as sr
from pydub import AudioSegment
import re
import sys
import os

from modules.web import set_command, finish_command
from constants import State, AUDIO_FOLDER
from voiceIdent import predict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AudioProcessingError(Exception):
    """Excepción personalizada para errores en el procesamiento de audio."""
    pass

class SpeechRecognitionError(Exception):
    """Excepción personalizada para errores en el reconocimiento de voz."""
    pass

def extract_degrees(text):
    """
    Extracts the degree value from a given text string.

    Parameters:
        text (str): The text containing the degree information.

    Returns:
        int or None: The extracted degree value if found, otherwise None.
    """
    match = re.search(r'gira (\d+)º', text)
    if match:
        return int(match.group(1))
    match = re.search(r'gira (\d+) grados', text)
    if match:
        return int(match.group(1))
    return None

async def recognize_audio(file_path):
    """
    Recognizes audio from a WAV file using the Google Speech Recognition API.

    Parameters:
        file_path (str): The path to the WAV file.

    Returns:
        str: The recognized text from the audio file.

    Raises:
        SpeechRecognitionError: If there is an error with speech recognition.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='es-ES')
                return text
            except sr.UnknownValueError:
                raise SpeechRecognitionError("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                raise SpeechRecognitionError(f"Could not request results from Google Speech Recognition; {e}")
    except Exception as e:
        raise AudioProcessingError(f"Error processing the audio file: {e}")

async def recognize_audio_from_file(file_path, state=State.STANDBY, audio_folder=AUDIO_FOLDER):
    """
    Recognizes audio from a file and performs actions based on the recognized text.

    Parameters:
        file_path (str): The path to the audio file.
        state (State): The current state of the system.
        audio_folder (str): The folder containing audio files.

    Returns:
        State: The new state of the system based on the recognized command.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(file_path, format="wav")
    except Exception as e:
        raise AudioProcessingError(f"Error exporting audio file: {e}")

    try:
        person, t = predict(audio=file_path)
        print("Persona identificada:", person, "en tiempo:", t)
    except Exception as e:
        raise AudioProcessingError(f"Error predicting audio file: {e}")

    if person == 4:
        return state

    try:
        text = await recognize_audio(file_path)
        print("Texto reconocido:", text)
    except SpeechRecognitionError as e:
        print(e)
        return state
    except AudioProcessingError as e:
        print(e)
        return state

    if text is None:
        return state

    return await handle_state_transitions(state, text, file_path, person, audio_folder)

async def handle_state_transitions(state, text, file_path, person, audio_folder):
    """
    Handles transitions between different states based on recognized text.

    Parameters:
        state (State): The current state of the system.
        text (str): The recognized text.
        file_path (str): The path to the audio file.
        person (str): The identified person.
        audio_folder (str): The folder containing audio files.

    Returns:
        State: The new state of the system after processing the text command.
    """
    if state == State.STANDBY:
        return await standby_state(text, file_path, person, state)

    elif state == State.WALK:
        return await walk_state(text, file_path, person, state, audio_folder)

    elif state == State.SIT:
        return await sit_state(text, file_path, person, state)

    elif state == State.STANDUP:
        return await standup_state(text, file_path, person, state, audio_folder)

    elif state == State.ROTATE:
        return await rotate_state(text, file_path, person, state, audio_folder)
    
    else:
        return state


async def standby_state(text, file_path, person, state):
    """
    Processes commands in the standby state.

    Parameters:
        text (str): The recognized text.
        file_path (str): The path to the audio file.
        person (str): The identified person.
        state (State): The current state of the system.

    Returns:
        State: The new state of the system after processing the command.
    """
    if "siéntate" in text:
        res = await set_command(file_path, person, text, State.SIT)
        return State.SIT if res else state

    elif "ven aquí" in text:
        res = await set_command(file_path, person, text, State.WALK)
        return State.WALK if res else state

    elif "gira" in text:
        degrees = extract_degrees(text)
        print("Grados de giro:", degrees)
        if degrees is not None:
            res = await set_command(file_path, person, text, State.ROTATE)
            return (State.ROTATE, degrees) if res else state
        else:
            return state
    else:
        return state

async def walk_state(text, file_path, person, state, audio_folder):
    """
    Processes commands in the walk state.

    Parameters:
        text (str): The recognized text.
        file_path (str): The path to the audio file.
        person (str): The identified person.
        state (State): The current state of the system.
        audio_folder (str): The folder containing audio files.

    Returns:
        State: The new state of the system after processing the command.
    """
    if "gira" in text:
        degrees = extract_degrees(text)
        print("Grados de giro:", degrees)
        if degrees is not None:
            res = await set_command(file_path, person, text, State.ROTATE)
            return (State.ROTATE, degrees) if res else state
        else:
            return state

    elif ("para" in text) or ("stop" in text) or ("termina" in text):
        if await finish_command():
            await cleanup_files(audio_folder=audio_folder)
            return State.STANDBY

    elif "siéntate" in text:
        res = await set_command(file_path, person, text, State.SIT)
        return State.SIT if res else state
    
    else:
        return state

async def sit_state(text, file_path, person, state):
    """
    Processes commands in the sit state.

    Parameters:
        text (str): The recognized text.
        file_path (str): The path to the audio file.
        person (str): The identified person.
        state (State): The current state of the system.

    Returns:
        State: The new state of the system after processing the command.
    """
    if "levántate" in text:
        res = await set_command(file_path, person, text, State.STANDUP)
        return State.STANDUP if res else state
    else:
        return state

async def standup_state(text, file_path, person, state, audio_folder):
    """
    Processes commands in the standup state.

    Parameters:
        text (str): The recognized text.
        file_path (str): The path to the audio file.
        person (str): The identified person.
        state (State): The current state of the system.
        audio_folder (str): The folder containing audio files.

    Returns:
        State: The new state of the system after processing the command.
    """
    if ("termina" in text) or ("para" in text) or ("stop" in text):
        if await finish_command():
            await cleanup_files(audio_folder=audio_folder)
            return State.STANDBY

    elif "ven aquí" in text:
        res = await set_command(file_path, person, text, State.WALK)
        return State.WALK if res else state

    elif "siéntate" in text:
        res = await set_command(file_path, person, text, State.SIT)
        return State.SIT if res else state

    elif "gira" in text:
        degrees = extract_degrees(text)
        print("Grados de giro:", degrees)
        if degrees is not None:
            res = await set_command(file_path, person, text, State.ROTATE)
            return (State.ROTATE, degrees) if res else state
        else:
            return state

    else:
        return state

async def rotate_state(text, file_path, person, state, audio_folder):
    """
    Rotates the state based on the given text command.

    Parameters:
    - text (str): The text command received.
    - file_path (str): The file path.
    - person (str): The person's name.
    - state (State): The current state.
    - audio_folder (str): The folder path for audio files.

    Returns:
    - State: The updated state after rotating.

    """
    if ("termina" in text) or ("para" in text) or ("stop" in text):
        if await finish_command():
            await cleanup_files(audio_folder=audio_folder)
            return State.STANDBY

    elif "siéntate" in text:
        res = await set_command(file_path, person, text, State.SIT)
        return State.SIT if res else state

    elif "ven aquí" in text:
        res = await set_command(file_path, person, text, State.WALK)
        return State.WALK if res else state

    else:
        return state

async def process_files(audio_folder=AUDIO_FOLDER, state=State.STANDBY):
    """
    Process audio files in the specified folder.

    Parameters:
        audio_folder (str): Path to the folder containing audio files. Default is `AUDIO_FOLDER`.
        state (State): The current state of the system.

    Returns:
        State: The final state after processing all files.

    Raises:
        AudioProcessingError: If there is an error while processing audio files.
    """
    archivos = os.listdir(audio_folder)
    res = state
    for archivo in archivos:
        if archivo.lower().endswith('.wav'):
            print(f"Nuevo archivo WAV detectado: {archivo}")
            ruta_archivo = os.path.join(audio_folder, archivo)
            try:
                res = await recognize_audio_from_file(ruta_archivo, state, audio_folder=audio_folder)
            except AudioProcessingError as e:
                print(f"Error al procesar el archivo de audio: {e}")
            except Exception as e:
                print(f"Error inesperado: {e}")
            try:
                if len(os.listdir(audio_folder)) > 0:
                    os.remove(ruta_archivo)
                    print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")
    return res

async def cleanup_files(audio_folder=AUDIO_FOLDER):
    """
    Clean up audio files in the specified folder.

    This function removes all audio files with the '.wav' extension from the specified folder.

    Parameters:
        audio_folder (str): The folder containing audio files.

    Returns:
        None

    Raises:
        OSError: If there is an error while removing the file.
    """
    archivos = os.listdir(audio_folder)
    for archivo in archivos:
        if archivo.lower().endswith('.wav'):
            ruta_archivo = os.path.join(audio_folder, archivo)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo {archivo} eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo}: {e}")
