#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN
import sys, os
class State:
    CONNECT = 0
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

class MotionState: 
    PASO0 = 0
    PASO1 = 1
    PASO2 = 2
    
#-----------------------------------------------------------------------
#Definición de constantes

AUDIO_FOLDER = os.path.abspath('../webServer/uploads')
SERVER = "https://localhost:3000"

MPU6050_ADDR = 0x68

LED_PIN_GREEN = 17  
LED_PIN_RED = 18
LED_PIN_YELLOW = 24

#Pasos del movimiento de andar 
# Ángulos de las articulaciones (en grados) para los dos pasiciones, no se guardan directamente los angulos de los servos para hacerlo
# mas ordenado y tener una referencia de los angulos de las articulaciones y no de los servos
WALK = [
    (165, 145),  # Paso 4
    (180, 95)   # Paso 5 (volver al paso inicial)
]


L1 = 13.5
L2 = 17

MESSAGE_AUDIO = 0
MESSAGE_WALK = 1

INIT_DERECHA_SUP = 45
INIT_DERECHA_INF = 50
INIT_IZQUIERDA_SUP = 145
INIT_IZQUIERDA_INF = 130

INIT = [INIT_DERECHA_SUP, INIT_DERECHA_INF, INIT_IZQUIERDA_SUP, INIT_IZQUIERDA_INF]

COMANDOS_STANDUP = [{
        str(Axis.DERECHO_SUP): 10,
        str(Axis.IZQUIERDO_SUP): 180
    },{
        str(Axis.DERECHO_INF): 30,
        str(Axis.IZQUIERDO_INF): 150
    },{
        str(Axis.DERECHO_SUP): 45,
        str(Axis.IZQUIERDO_SUP): 145
    },{
        str(Axis.DERECHO_INF): 50,
        str(Axis.IZQUIERDO_INF): 130
    
    }
]

COMANDOS_SIT = [{
        str(Axis.DERECHO_INF): 30,
        str(Axis.IZQUIERDO_INF): 150
    },{
        str(Axis.DERECHO_INF): 0,
        str(Axis.IZQUIERDO_INF): 180
    }
]


#matriz de calibración de los angulos de las articulaciones y los servos, para tener una referencia de el angulo del esquema vs el angulo del servo
CALIBRATIONS = {
    Axis.IZQUIERDO_SUP: {
        'joint_angle_ref': 180,
        'servo_angle_ref': 145,
    },
    Axis.IZQUIERDO_INF: {
        'joint_angle_ref': 95,
        'servo_angle_ref': 130,
    },
    Axis.DERECHO_SUP: {
        'joint_angle_ref': 180,
        'servo_angle_ref': 45,
    },
    Axis.DERECHO_INF: {
        'joint_angle_ref': 95,
        'servo_angle_ref': 50,
    },
    Axis.DELANTERO: {
        'joint_angle_ref': 0,
        'servo_angle_ref': 84,
    }
}

DERECHA = 0
IZQUIERDA = 1
ALL = 2


TIME_SLEEP = 0.7

TRIG = 23
ECHO = 25