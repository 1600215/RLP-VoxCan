import serial
import time
import json
import math
import mpu6050
import sys
import numpy as np
import RPi.GPIO as GPIO



#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN
# The above code defines classes for state, command, status, and axis constants in a Python program.

class State:
    INITIALIZE = 0
    CONNECTING = 1
    CALIBRATION = 2
    STANDBY = 3
    COMMAND = 4

class Command:
    CONNECT = 0
    GET_POS = 1
    SET_POS = 2
    
class Status:
    CONNECTED = 0
    RECIVED = 1
    
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

def calcular_desbalanceo():
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

def connect():
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
    recv = json.loads(recv)
                    
    if "status" in recv and recv["status"] == Status.CONNECTED:
        print("Arduino Nano comunicado")
        return True
                    
    print("Error al comunicar con el Arduino Nano - volvemos a intentar")
    return False
    

#-----------------------------------------------------------------------
#Función para obtener la posición de los servos

def getPos():
    '''The `getPos` function sends a command to a serial device to retrieve position data and returns the
    initial position received.
    
    Returns
    -------
        The `getPos()` function returns the initial position received from the serial port after sending a
    command to get the position.
    
    '''
    
    command = {'command': Command.GET_POS}
    ser.write(json.dumps(command).encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    
    initialPos = json.loads(ser.readline().decode().strip())
    
    if "status" in initialPos and initialPos["status"] == Status.RECIVED:
        return initialPos['parametros']
    
    return initialPos         


#-----------------------------------------------------------------------
#Función para enviar los parámetros de los servos

def setPos(params):
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
    ser.write(json.dumps(command).encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    
    recv = json.loads(ser.readline().decode().strip())
    print(recv)
    if(recv["status"] == Status.RECIVED):
        incl_x, incl_y = calcular_desbalanceo()
        return incl_x, incl_y
    
    return None, None  

#-----------------------------------------------------------------------
#Función para calibrar los servos

def calibrate_servos():
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
    initialPos = getPos()  
                
    axisDS = np.arange(initialPos[str(Axis.DERECHO_SUP)] - 10, initialPos[str(Axis.DERECHO_SUP)] + 10, 1) 
    axisDI= np.arange(initialPos[str(Axis.DERECHO_INF)] - 10, initialPos[str(Axis.DERECHO_INF)] + 10, 1)   
    axisIS = np.arange(initialPos[str(Axis.IZQUIERDO_SUP)] - 10, initialPos[str(Axis.IZQUIERDO_SUP)] + 10, 1)   
    axisII = np.arange(initialPos[str(Axis.IZQUIERDO_INF)] - 10, initialPos[str(Axis.IZQUIERDO_INF)] + 10, 1)  

    for angulo_eje_1 in axisDS:
        for angulo_eje_2 in axisDI:
            for angulo_eje_3 in axisIS:
                for angulo_eje_4 in axisII:
                    try:
                        incl_x, incl_y = setPos({str(Axis.DERECHO_SUP) : angulo_eje_1, str(Axis.DERECHO_INF) : angulo_eje_2, str(Axis.IZQUIERDO_SUP) : angulo_eje_3, str(Axis.IZQUIERDO_INF) : angulo_eje_4})
                    
                              
                        if incl_x is None or incl_y is None:
                            print("Error al enviar los parámetros de los servos")
                            sys.exit(1)
                                    
                        if abs(incl_x) + abs(incl_y) < min:
                            min = abs(incl_x) + abs(incl_y)
                            config = {str(Axis.DERECHO_SUP) : angulo_eje_1, str(Axis.DERECHO_INF) : angulo_eje_2, str(Axis.IZQUIERDO_SUP) : angulo_eje_3, str(Axis.IZQUIERDO_INF) : angulo_eje_4}
                                    
                    except Exception as e:
                        print("Error al enviar los parámetros de los servos:", e)
                        sys.exit(1)
    return config


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
                
                # Enviar el comazndo de conexión al Arduino 
                try:
                    if connect():
                        current_state = State.CALIBRATION
                    else:
                        print("Error al conectar con el Arduino Nano")
                        if time.time() - t > 5:
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
            
            standby_params = calibrate_servos()
            
            print("Calibración finalizada")
            print("Parámetros de calibración:", standby_params)
            
            _, _ = setPos(standby_params)

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


            #Diagrama de estado para reconocmiento e identsificación de voz para los comandos 

            #Recibe mp3 cada 3s
            #current_state = State.COMMAND
            
            
        #-----------------------------------------------------------------------
        elif current_state == State.COMMAND:

                current_state = State.STANDBY
            
        #-----------------------------------------------------------------------
        else:
            print("Error")

    except Exception as e:
        print("Error en el bucle funcional:", e)
        break
