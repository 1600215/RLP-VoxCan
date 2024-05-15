import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO
import speech_recognition as sr
from pydub import AudioSegment
import joblib
import librosa
import cv2


#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN
# The above code defines classes for state, command, status, and axis constants in a Python program.

class State:
    INITIALIZE = 0
    CALIBRATION = 1
    STANDBY = 2
    SIT = 3
    COME = 4

class Command:
    CONNECT = 0
    GET_POS = 1
    SET_POS = 2
    
class Status:
    OK = 0
    ERROR = 1
    
class Axis:
    DERECHO_SUP = 0
    DERECHO_INF = 1
    IZQUIERDO_SUP = 2
    IZQUIERDO_INF = 3
    DELANTERO = 4        


#-----------------------------------------------------------------------
#Definición de constantes y variables globalesº


MPU6050_ADDR = 0x68

LED_PIN_GREEN = 17  
LED_PIN_RED = 18
LED_PIN_YELLOW = 24


current_state = State.INITIALIZE
standby_params = None
recognizer = sr.Recognizer()
modelo = joblib.load('modelo_preentrenado.pkl')

#-----------------------------------------------------------------------
#Inicialización de los pines GPIO de los leds 

try: 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN_GREEN, GPIO.OUT) # LED1
    GPIO.setup(18, GPIO.OUT)  # LED2
    GPIO.setup(24, GPIO.OUT)  # LED3
    
    try: 
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        GPIO.output(LED_PIN_YELLOW, GPIO.LOW)
    except Exception as e: 
        print("Error al poner los pines GPIO de los leds VERDE Y AMARILLO en bajo y ROJO eb alto en la fase inicia", e)
        sys.exit(1)
        
except Exception as e: 
    print("Error al inicializar los pines GPIO de los leds", e)
    sys.exit(1)


#-----------------------------------------------------------------------
# Inicialización del puerto serie y del mpu6050

try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

except Exception as e:
    print("Error de comunicación serial con Arduino Nano:", e)
    sys.exit(1)

#-----------------------------------------------------------------------
#Inicialización del MPU6050
try:
    mpu = mpu6050.mpu6050(MPU6050_ADDR)
    
except Exception as e:
    print("Error al inicializar el MPU6050:", e)
    sys.exit(1)
    
    


#-----------------------------------------------------------------------
#Función para caluclar el desbalanceo en los ejes x y y

def calcular_desbalanceo(mpu):
    '''This Python function calculates the imbalance in both x and y axes based on accelerometer data.
    
    Returns
    -------
        The function `calcular_desbalanceo` is returning the angles of inclination in both the x and y axes
    calculated from the accelerometer data. The values `inclinacion_x` and `inclinacion_y` represent the
    tilt angles in degrees for the x and y axes respectively.
    
    '''
    
    # Leer datos del acelerómetro y el giroscopio
    acelerometro = mpu.get_accel_data()

    # Calcular ángulo de inclinación en cada eje a partir del acelerómetro
    inclinacion_x = math.atan2(acelerometro['y'], acelerometro['z']) * 180 / math.pi
    inclinacion_y = math.atan2(-acelerometro['x'], math.sqrt(acelerometro['y']**2 + acelerometro['z']**2)) * 180 / math.pi


    # Devolver desbalanceo en ambos ejes
    return inclinacion_x, inclinacion_y


#-----------------------------------------------------------------------
#Función para enviar el comando de conexión al arduino nano

def connect(ser):
    '''The `connect` function establishes communication with an Arduino Nano and returns True if
    successful, otherwise returns False.
    
    Returns
    -------
        The `connect()` function returns a boolean value - `True` if the communication with the Arduino
    Nano was successful and it is connected, and `False` if there was an error in communication or the
    connection was not successful.
    
    '''

    res = {'command' : Command.CONNECT}
    ser.write(json.dumps(res).encode('utf-8'))
    ser.flush()
                    
    while ser.in_waiting == 0:
        pass
                    
    recv = ser.readline().decode('utf-8').rstrip()
    
    
    try:
        recv = json.loads(recv)
    except:    
        print("Error al cargar el json - volvemos a intentar")
        return False
        
    if "status" in recv and recv["status"] == Status.OK:
        print("Arduino Nano comunicado")
        return True
                    
    print("Error al comunicar con el Arduino Nano - volvemos a intentar")
    return False
    

#-----------------------------------------------------------------------
#Función para obtener la posición de los servos

def getPos(ser):
    '''The `getPos` function sends a command to a serial device to retrieve position data and returns the
    initial position received.
    
    Returns
    -------
        The `getPos()` function returns the initial position received from the serial port after sending a
    command to get the position.
    
    {"0" : 90, "1" : 90, "2" : 90, "3" : 90, "4" : 90}
    
    '''
    
    command = {'command': Command.GET_POS}
    ser.write((json.dumps(command) + '\n').encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    try:
        initialPos = json.loads(ser.readline().decode().rstrip())
    except:
        print("Error al cargar el json")
        return None
    
    if "status" in initialPos and initialPos["status"] == Status.OK:
        return initialPos['posiciones']
    
    return None         


#-----------------------------------------------------------------------
#Función para enviar los parámetros de los servos

def setPos(ser,mpu,params):
    '''The function `setPos` sends a command to a serial device, waits for a response, and returns
    calculated values based on the response.
    
    Parameters
    ----------
    params
        It seems like the code snippet you provided is a function named `setPos` that sends a command to a
    serial device, waits for a response, and then processes the response based on the status received.
    
    Returns
    -------
        The function `setPos` is returning a tuple of values `incl_x, incl_y` if the received status is
    `RECIVED`. Otherwise, it returns `None, None`.
    
    '''
    
    command = {'command': Command.SET_POS, 'parametros': params}
    
    ser.write((json.dumps(command)+ '\n').encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    
    recv = json.loads(ser.readline().decode().rstrip())
    print(recv)
    if(recv["status"] == Status.OK):
        incl_x, incl_y = calcular_desbalanceo(mpu)
        return incl_x, incl_y
    
    return None, None  

#-----------------------------------------------------------------------
#Función para calibrar los servos

def calibrate_servos(ser, mpu):
    '''This Python function calibrates servo motors by iterating through different angles for each axis and
    finding the configuration that minimizes the sum of inclinations in the x and y directions.
    
    Returns
    -------
        The function `calibrate_servos` is returning a dictionary `config` containing the calibrated
    positions for each servo axis (DERECHO_SUP, DERECHO_INF, IZQUIERDO_SUP, IZQUIERDO_INF) that resulted
    in the minimum absolute sum of inclinations in the x and y directions.
    
    '''
    min = sys.float_info.max
    config = None
    initialPos = getPos(ser)  
    
    if initialPos is None:
        print("Error al obtener la posición inicial de los servos")
        return None
    
    axisDS = np.arange(initialPos[str(Axis.DERECHO_SUP)] - 10, initialPos[str(Axis.DERECHO_SUP)] + 10, 1) 
    axisDI= np.arange(initialPos[str(Axis.DERECHO_INF)] - 10, initialPos[str(Axis.DERECHO_INF)] + 10, 1)   
    axisIS = np.arange(initialPos[str(Axis.IZQUIERDO_SUP)] - 10, initialPos[str(Axis.IZQUIERDO_SUP)] + 10, 1)   
    axisII = np.arange(initialPos[str(Axis.IZQUIERDO_INF)] - 10, initialPos[str(Axis.IZQUIERDO_INF)] + 10, 1)  

    for angulo_eje_1 in axisDS:
        for angulo_eje_2 in axisDI:
            for angulo_eje_3 in axisIS:
                for angulo_eje_4 in axisII:
                    try:
                        incl_x, incl_y = setPos(ser,mpu,  {str(Axis.DERECHO_SUP) : angulo_eje_1, str(Axis.DERECHO_INF) : angulo_eje_2, str(Axis.IZQUIERDO_SUP) : angulo_eje_3, str(Axis.IZQUIERDO_INF) : angulo_eje_4})
                             
                        if incl_x is None or incl_y is None:
                            print("Error al enviar los parámetros de los servos")
                            sys.exit(1)
                                    
                        if abs(incl_x) + abs(incl_y) < min:
                            min = abs(incl_x) + abs(incl_y)
                            config = {str(Axis.DERECHO_SUP) : angulo_eje_1, str(Axis.DERECHO_INF) : angulo_eje_2, str(Axis.IZQUIERDO_SUP) : angulo_eje_3, str(Axis.IZQUIERDO_INF) : angulo_eje_4}
                                    
                    except Exception as e:
                        print("Error al enviar los parámetros de los servos:", e)
                        sys.exit(1)
    return None

#-----------------------------------------------------------------------
#Función para convertir audio a mp3

def convert_audio_to_mp3(audio_data, output_filename):
    '''The function `convert_audio_to_mp3` takes audio data, converts it to raw audio data, creates an
    AudioSegment, and exports it to an MP3 file.
    
    Parameters
    ----------
    audio_data
        The `audio_data` parameter in the `convert_audio_to_mp3` function is an object that represents
    audio data. It seems like it has a method `get_raw_data()` that retrieves the raw audio data from
    the object. This raw audio data is then used to create an `AudioSegment`
    output_filename
        The `output_filename` parameter is a string that represents the name of the file where the
    converted audio will be saved as an MP3 file. It should include the file extension ".mp3" at the
    end.
    
    '''
    # Convert AudioData to raw audio data
    raw_audio_data = audio_data.get_raw_data()
    sample_rate = 44100 #Depende del micrófono
    canales = 1 #También depende del micrófono

    # Convert raw audio data to AudioSegment
    audio_segment = AudioSegment(
        raw_audio_data,
        sample_width=audio_data.sample_width,
        frame_rate=sample_rate,
        channels=canales
    )
    
    # Export AudioSegment to MP3
    audio_segment.export(output_filename, format="mp3")


#-----------------------------------------------------------------------
#Función para hacer ventana deslizante de una imagen

def windowing(image, max_size):
    '''The function `windowing` creates a matrix of windows from an image by rearranging its columns.
    
    Parameters
    ----------
    image
        The `image` parameter is a 2D numpy array representing an image. Each element in the array
    corresponds to a pixel value in the image.
    max_size
        The `max_size` parameter in the `windowing` function represents the maximum size of the window
    matrix that will be created. This parameter determines the number of rows in the window matrix,
    while the number of columns will be the same as the number of columns in the input `image` array.
    
    Returns
    -------
        a matrix of windows with a maximum size specified by the `max_size` parameter. Each window is a
    column from the input `image` matrix.
    
    '''
    windows = np.zeros((max_size, image.shape[0]))  # Crear matriz de ventanas con el mismo número de columnas que la imagen
    for i in np.arange(0, image.shape[1]):
        windows[ i, :] = image[: , i]
    return windows


#-----------------------------------------------------------------------
#Función para identificar la persona de un audio

def reconocer_comando_voz(audio, modelo):
    '''The `reconocer_comando_voz` function recognizes voice commands using a pre-trained model and
    returns the recognized command.
    
    Parameters
    ----------
    audio
        The `audio` parameter is the audio data containing the voice command that needs to be
    recognized. It is passed to the pre-trained model for recognition.
    modelo
        The `modelo` parameter is the pre-trained model that is used to recognize the voice command
    from the audio data.
    
    Returns
    -------
        The `reconocer_comando_voz` function returns the recognized voice command as a string.
    
    '''
    
    #Preprocesamiento
    y, sr = librosa.load(audio)
    y = librosa.effects.trim(y)[0]
    image = librosa.feature.melspectrogram(y=y, sr=sr)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    windows = windowing(image, 320)

    #Prediccion
    persona = modelo.predict(windows)
    
    return persona



#-----------------------------------------------------------------------
#Bucle principal de la Raspberry Pi

t = time.time()

while True:
    try: 
        
        #-----------------------------------------------------------------------
        #Estado inicial para realizar conexión con el arduino nano
        
        if current_state == State.INITIALIZE:
            #si la conexión con el Arduino Nano está abierta
            if ser.isOpen():
                
                print("Arduino Nano conectado")

                time.sleep(1) # Esperar a que el puerto serie se abra correctamente
                
                # Enviar el comazndo de conexión al Arduino 
                try:
                    if connect(ser):
                        current_state = State.CALIBRATION
                    else:
                        print("Error al conectar con el Arduino Nano")
                        if time.time() - t > 10:
                            print("Error al conectar con el Arduino Nano")
                            break
                        
                except Exception as e:
                    print("Error al comunicarse con Arduino nano:", e)
                    break
            

        #-----------------------------------------------------------------------
        #Estado de calibración de los servos
        #Se utiiliza el led amarillo para indicar que se está calibrando los servos
        
        elif current_state == State.CALIBRATION:
                  
            try: 
                GPIO.output(LED_PIN_RED, GPIO.LOW)
                GPIO.output(LED_PIN_YELLOW, GPIO.HIGH)
                print("Calibrando servos...")

            except Exception as e:
                print("Error al poner el pin GPIO del led verde en bajo y el amarillo en alto", e)
                sys.exit(1)
            
            standby_params = calibrate_servos(ser, mpu)
            
            if standby_params is None:
                print("Error al calibrar los servos")
                sys.exit(1)
            
            print("Calibración finalizada")
            print("Parámetros de calibración:", standby_params)
            
            _, _ = setPos(ser, standby_params)

            try:
                GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                GPIO.output(LED_PIN_RED, GPIO.LOW)
                
            except Exception as e:
                print("Error al poner el pin GPIO del led verde en alto y el rojo en bajo", e)
                sys.exit(1)
            
            current_state = State.STANDBY
            
        #-----------------------------------------------------------------------    
        elif current_state == State.STANDBY:
            print("Esperando comando desde la Raspberry Pi...")


            #Bucle de audio
            while True:
                with sr.Microphone() as source:
                    print("Listening...")
                    audio = recognizer.listen(source)
                    
                try:
                    print("Recognizing...")
                    text = recognizer.recognize_google(audio, language="es-ES")
                    print("You said:", text)
                    if "siéntate" in text:                  
                        convert_audio_to_mp3(audio, "sientate.mp3")
                        persona = reconocer_comando_voz("sientate.mp3", modelo)
                        if persona == 0 or persona == 1 or persona == 2 or persona == 3:
                            current_state = State.SIT
                            break
                        
                    elif "ven" in text:                  
                        convert_audio_to_mp3(audio, "ven.mp3")
                        persona = reconocer_comando_voz("ven.mp3", modelo)
                        if persona == 0 or persona == 1 or persona == 2 or persona == 3:
                            current_state = State.COME
                            break
                
                except sr.UnknownValueError:
                    print("Sorry, I couldn't understand what you said.")
                except sr.RequestError as e:
                    print("Sorry, there was an error with the speech recognition service:", str(e))            


        #-----------------------------------------------------------------------
        elif current_state == State.SIT:
            try:
                GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
                                
            except Exception as e:
                print("Error al poner el pin GPIO del led verde en alto", e)
                sys.exit(1)
            current_state = State.STANDBY
        
        #-----------------------------------------------------------------------
        elif current_state == State.COME:
            try:
                GPIO.output(LED_PIN_RED, GPIO.HIGH)
                                
            except Exception as e:
                print("Error al poner el pin GPIO del led rojo en alto", e)
                sys.exit(1)
            current_state = State.STANDBY

        #-----------------------------------------------------------------------
        else:
            print("Error")

    except Exception as e:
        print("Error en el bucle funcional:", e)
        break
