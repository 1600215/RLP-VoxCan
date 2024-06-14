#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN
import sys, os
class State:
    INITIALIZE = 0
    SET_INIT = 1
    CALIBRATION = 2
    STANDBY = 3
    SIT = 4
    WALK = 5    
    ROTATE = 7
    STANDUP = 8

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

AUDIO_FOLDER = os.path.abspath('../webServer/uploads')
SERVER = "https://localhost:3000"


MPU6050_ADDR = 0x68

LED_PIN_GREEN = 17  
LED_PIN_RED = 18
LED_PIN_YELLOW = 24

#Pasos del movimiento de andar 
# Ángulos de las articulaciones (en grados) para los cinco pasos
WALK = [
    (155, 100),   # Paso 2
    (155, 145),   # Paso 3
    (175, 145),  # Paso 4
    (175, 100)   # Paso 5 (volver al paso inicial)
]


L1 = 13.5
L2 = 17


DERECHA = 0
IZQUIERDA = 1