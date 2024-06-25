import speech_recognition as sr
from pydub import AudioSegment
import re
import sys
import os

from modules.web import set_command, go_standby
from constants import State, AUDIO_FOLDER, MESSAGE_WALK, MESSAGE_AUDIO
from voiceIdent import predict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
                return None
            except sr.RequestError as e:
                raise Exception(f"Error en la solicitud de reconocimiento de voz: {e}")
    except Exception as e:
        raise Exception(f"Error al abrir el archivo de audio: {e}")

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
        raise Exception(f"Error exporting audio file: {e}")
    try:
        person, t = predict(audio=file_path)
        print("Persona identificada:", person, "en tiempo:", t)
    except Exception as e:
        raise Exception(f"Error predicting audio file: {e}")

    if person == 4:
        return state

    try:
        text = await recognize_audio(file_path)
        print("Texto reconocido:", text)
    except Exception as e:
        raise Exception(f"Error recognizing audio file: {e}")

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

    elif ("ven aquí" in text) or ("camina" in text):
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
        if await go_standby():
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
        if await go_standby():
            await cleanup_files(audio_folder=audio_folder)
            return State.STANDBY

    elif ("ven aquí" in text) or ("camina" in text):
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
        if await go_standby():
            await cleanup_files(audio_folder=audio_folder)
            return State.STANDBY

    elif "siéntate" in text:
        res = await set_command(file_path, person, text, State.SIT)
        return State.SIT if res else state

    elif ("ven aquí" in text) or ("camina" in text):
        res = await set_command(file_path, person, text, State.WALK)
        return State.WALK if res else state

    else:
        return state

async def walkStop(queueWalk, audio_folder):
    """
    Stops the walking action and performs cleanup if the robot has collided.

    Args:
        queueWalk (Queue): The queue containing the walking messages.
        audio_folder (str): The path to the audio folder.

    Returns:
        bool: True if the walking action was stopped and cleanup was performed, False otherwise.
    """
    #comprueba que la cola que se comunica con el thread que ejecuta el movimiento no esta vacia
    if not queueWalk.empty():
        #recibit el comando
        income_message = await queueWalk.get()
        #si el comando es correcto
        if income_message == MESSAGE_WALK:
            #ves a estado STANDBY ya que se ha chocado
            if await go_standby():
                #limpia la carpeta uploads
                await cleanup_files(audio_folder=audio_folder)
                return True
    #devuelve false ya que no se ha chocado el robot
    return False
                    

async def process_files(audio_folder=AUDIO_FOLDER, state=State.STANDBY, queue=None):
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
    
    #varaibles locales para el correcto funcionamiento de la función
    archivos = os.listdir(audio_folder)
    res = state
    
    #comprobar comunicación entre movimiento y control de los estados con audio
    if state == State.WALK:
        if not isinstance(queue, tuple):
            return
        else: queueAudio, queueWalk = queue
    
    for archivo in archivos:
        
        ##comporbar que no se ha chocado el robot
        if state == State.WALK and await walkStop(queueWalk, audio_folder): return State.STANDBY

        if archivo.lower().endswith('.wav'):
            #detecta nueov archivo wav
            print(f"Nuevo archivo WAV detectado: {archivo}")
            ruta_archivo = os.path.join(audio_folder, archivo)
            
            try:
                #a partir del archivo. devuelve si hay una comanda de cambio de estado en funcion del estado actual y del audio
                res = await recognize_audio_from_file(ruta_archivo, state, audio_folder=audio_folder)
                
                #comprobar que pasa de WALK a OTRO_ESTADO, en caso afirmativo, mandar info a movimiento
                if state == State.WALK and res != State.WALK:
                    print("cambio de estado de  walk -> ", res)        
                    await queueAudio.put(MESSAGE_AUDIO)
            
            #escepcion si falla recognize_audio_from_file
            except Exception as e:
                raise Exception(f"Error al procesar el archivo de audio: {e}")
        
            try:
                #eliminar el archivo
                if len(os.listdir(audio_folder)) > 0:
                    os.remove(ruta_archivo)
                    print(f"Archivo {archivo} eliminado correctamente.")
                    
            #excpecion sobre la eliminacion del archivo
            except Exception as e:
                raise Exception(f"Error al eliminar el archivo {archivo}: {e}")
            
        #si ha cambiado de estado, no analizar mas audios
        if res != state:
            break

    #comprobar si no se ha chocado mientras se analizaba el ultimo audio
    if state == State.WALK and await walkStop(queueWalk, audio_folder): return State.STANDBY
    #si no se ha chocado el robot en caso de estar en estado WALK, devolver res
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
                raise Exception(f"Error al eliminar el archivo {archivo}: {e}")
