#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN

class State:
    INITIALIZE = 0
    SET_INIT = 1
    CALIBRATION = 2
    STANDBY = 3
    SIT = 4
    COME = 5
    

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
#Definición de constantes

AUDIO_FOLDER = "../webServer/uploads"
SERVER = "http://localhost:3000"


MPU6050_ADDR = 0x68

LED_PIN_GREEN = 17  
LED_PIN_RED = 18
LED_PIN_YELLOW = 24


#Sample rate del microfono todavia por descubrir
SAMPLE_RATE = None


