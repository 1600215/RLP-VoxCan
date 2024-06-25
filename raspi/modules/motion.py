import os, sys
import numpy as np
import asyncio, time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import Axis, L1, L2, DERECHA, IZQUIERDA, WALK, MotionState, COMANDOS_STANDUP, MESSAGE_AUDIO, INIT, COMANDOS_SIT, CALIBRATIONS, ALL, TIME_SLEEP
from modules.arduino import setPos

# Función de mapeo de ángulos
def map_angle_to_servo(servo_name, joint_angle):
    """
    Maps the joint angle to the corresponding servo angle based on the calibration values.

    Args:
        servo_name (str): The name of the servo.
        joint_angle (float): The joint angle to be mapped.

    Returns:
        float: The corresponding servo angle.

    Raises:
        None

    """
    calib = CALIBRATIONS[servo_name]
    
    if Axis.IZQUIERDO_SUP == servo_name:
        servo_angle = (calib['joint_angle_ref'] - joint_angle) + calib['servo_angle_ref']
    elif Axis.IZQUIERDO_INF == servo_name:
        servo_angle = (joint_angle - calib['joint_angle_ref']) + calib['servo_angle_ref']
    elif Axis.DERECHO_SUP == servo_name:
        servo_angle = (joint_angle - calib['joint_angle_ref']) + calib['servo_angle_ref']
    elif Axis.DERECHO_INF == servo_name:
        servo_angle = (calib['joint_angle_ref'] - joint_angle) + calib['servo_angle_ref']

    else:
        return None
    
    if servo_angle < 0 or servo_angle > 180:
        return None
    return servo_angle

# Función de mapeo de servo a ángulo
def map_servo_to_angle(servo_name, servo_angle):
    """
    Maps the servo angle to the corresponding joint angle based on the servo calibration.

    Args:
        servo_name (str): The name of the servo.
        servo_angle (float): The angle of the servo in degrees.

    Returns:
        float: The corresponding joint angle in degrees.

    Raises:
        None

    """
    if servo_angle < 0 or servo_angle > 180:
        return None
    
    calib = CALIBRATIONS[servo_name]
    
    if Axis.IZQUIERDO_SUP == servo_name:
        joint_angle = calib['joint_angle_ref'] + (calib['servo_angle_ref'] - servo_angle)
    elif Axis.IZQUIERDO_INF == servo_name:
        joint_angle = (servo_angle - calib['servo_angle_ref']) + calib['joint_angle_ref']
    elif Axis.DERECHO_SUP == servo_name:
        joint_angle = (servo_angle - calib['servo_angle_ref']) + calib['joint_angle_ref']
    elif Axis.DERECHO_INF == servo_name:
        joint_angle = calib['joint_angle_ref'] + (calib['servo_angle_ref'] - servo_angle)
    else:
        return None

    return joint_angle


def cinematica_directa(theta1, theta2):
    """
    Calculates the forward kinematics of a robotic leg given the joint angles.

    Parameters:
    theta1 (float): Angle of the first joint in degrees.
    theta2 (float): Angle of the second joint in degrees.

    Returns:
    tuple: A tuple containing two tuples. The first tuple represents the coordinates of the knee joint (x_rodilla, y_rodilla),
    and the second tuple represents the coordinates of the foot joint (x_pie, y_pie).
    """
    x_rodilla = L1 * np.cos(np.radians(theta1))
    y_rodilla = L1 * np.sin(np.radians(theta1))
    
    x_pie = x_rodilla + L2 * np.cos(np.radians(theta1 + theta2))
    y_pie = y_rodilla + L2 * np.sin(np.radians(theta1 + theta2))
    
    return (x_rodilla, y_rodilla), (x_pie, y_pie)

def cinematica_inversa(x_pie, y_pie, y_hip_new):
    """
    Calculates the inverse kinematics for a robotic leg.

    Parameters:
    - x_pie (float): The x-coordinate of the foot position.
    - y_pie (float): The y-coordinate of the foot position.
    - y_hip_new (float): The y-coordinate of the hip position.

    Returns:
    - theta1 (float): The angle of the first joint in degrees.
    - theta2 (float): The angle of the second joint in degrees.
    """
    d = np.sqrt(x_pie**2 + (y_pie - y_hip_new)**2)
    alpha = np.arctan2(y_pie - y_hip_new, x_pie)
    beta = np.arccos((L1**2 + d**2 - L2**2) / (2 * L1 * d))
    
    theta1 = np.degrees(alpha - beta)
    theta2 = np.degrees(np.arccos((L1**2 + L2**2 - d**2) / (2 * L1 * L2))) - 180
    
    return theta1, theta2


def bajar_cadera(type, desplazamiento_vertical):
    """
    Move the hip joint downwards to lower the leg.

    Args:
        type (str): The type of leg movement. Can be 'DERECHA' or 'IZQUIERDA'.
        servo1 (int): The value of the first servo.
        servo2 (iånt): The value of the second servo.
        desplazamiento_vertical (float): The vertical displacement value.
        calibrations (dict): A dictionary containing calibration values.

    Returns:
        tuple: A tuple containing the coordinates of the knee joint (rodilla_x, rodilla_y) and the angles of the servos (theta1_new, theta2_new).
    """
    
    if type == DERECHA: 
        theta1_inicial = map_servo_to_angle(Axis.DERECHO_SUP, INIT[Axis.DERECHO_SUP])
        theta2_inicial = map_servo_to_angle(Axis.DERECHO_INF, INIT[Axis.DERECHO_INF])
    elif type == IZQUIERDA:
        theta1_inicial = map_servo_to_angle(Axis.IZQUIERDO_SUP, INIT[Axis.IZQUIERDO_SUP])
        theta2_inicial = map_servo_to_angle(Axis.IZQUIERDO_INF, INIT[Axis.IZQUIERDO_INF])
    else:
        return None
    
    _, (x_pie, y_pie) = cinematica_directa(theta1_inicial, theta2_inicial)
    
    theta1_new, theta2_new = cinematica_inversa(x_pie, y_pie, desplazamiento_vertical)
    theta2_new = np.abs(theta2_new)
    
    if (theta1_new < 0):
        theta1_new = theta1_new + 360
    
    (rodilla_x, rodilla_y), _ = cinematica_directa(theta1_new, theta2_new)
    return (rodilla_x, rodilla_y), (theta1_new, theta2_new)


def setPosAngle(ser, leg, theta = (None, None)):
    """
    Sets the position angle for a leg or all legs of a robot.

    Args:
        ser (object): The serial object used for communication with the robot.
        leg (int): The leg number or ALL to set the position angle for all legs.
        theta (tuple): The angle values for the leg(s) in the form (theta1, theta2).

    Returns:
        bool: True if the position angle is set successfully, False otherwise.
    """
    theta1, theta2 = theta
    if theta1 is None or theta2 is None:
        return False
    
    if leg == ALL:
        servo1D = map_angle_to_servo(Axis.DERECHO_SUP, theta1)
        servo2D = map_angle_to_servo(Axis.DERECHO_INF, theta2)
        
        servo1I = map_angle_to_servo(Axis.IZQUIERDO_SUP, theta1)
        servo2I = map_angle_to_servo(Axis.IZQUIERDO_INF, theta2)
        
        #comprueba que el mapeado ha sido correcto
        if servo1D is None or servo2D is None or servo1I is None or servo2I is None:
            return False

        #setPos a la posición paso
        return setPos(ser, {str(Axis.DERECHO_SUP): servo1D, str(Axis.DERECHO_INF): servo2D, str(Axis.IZQUIERDO_SUP): servo1I, str(Axis.IZQUIERDO_INF): servo2I})
    
    if leg == DERECHA:
        servo1 = map_angle_to_servo(Axis.DERECHO_SUP, theta1)
        servo2 = map_angle_to_servo(Axis.DERECHO_INF, theta2)
        
        #comprueba que el mapeado ha sido correcto
        if servo1 is None or servo2 is None:
            return False

        #setPos a la posición paso
        return setPos(ser, {str(Axis.DERECHO_SUP): servo1, str(Axis.DERECHO_INF): servo2})
    if leg == IZQUIERDA:
        servo1 = map_angle_to_servo(Axis.IZQUIERDO_SUP, theta1)
        servo2 = map_angle_to_servo(Axis.IZQUIERDO_INF, theta2)
        
        #comprueba que el mapeado ha sido correcto
        if servo1 is None or servo2 is None:
            return False
        
        #setPos a la posició paso
        return setPos(ser, {str(Axis.IZQUIERDO_SUP): servo1, str(Axis.IZQUIERDO_INF): servo2})
    
def switch_leg(leg):
    """
    Switches the leg parameter to the opposite leg.

    Parameters:
    leg (str): The leg to switch. Must be either 'DERECHA' or 'IZQUIERDA'.

    Returns:
    str: The opposite leg. Returns 'IZQUIERDA' if 'DERECHA' is passed, and vice versa.
    None: If an invalid leg is passed.
    """
    if (leg == DERECHA): return IZQUIERDA
    if (leg == IZQUIERDA): return DERECHA
    else: return None
    
async def loop_bajar_cadera(ser, leg, release=False):
    """
    Loop to gradually lower the leg's hip joint.

    Args:
        lock (asyncio.Lock): Lock to synchronize access to shared resources.
        leg (int): Leg identifier.
        calibrations (dict): Dictionary containing calibration values.

    Raises:
        Exception: If there is an error while calculating inverse kinematics or setting position.

    Returns:
        None
    """
    
    #opcion para bajar la cadera directamente
    if release:
        _ , (theta1, theta2) = bajar_cadera(leg, -2)
        if not setPosAngle(ser, leg, theta=(theta1, theta2)):
                raise Exception("Error while setting position in loop_bajar_cadera")
        await asyncio.sleep(0.2)
        _ , (theta1, theta2) = bajar_cadera(leg, -4)        
        if not setPosAngle(ser, leg, theta=(theta1, theta2)):
                raise Exception("Error while setting position in loop_bajar_cadera")
        await asyncio.sleep(0.2)
        _ , (theta1, theta2) = bajar_cadera(leg, -6)        
        if not setPosAngle(ser, leg, theta=(theta1, theta2)):
                raise Exception("Error while setting position in loop_bajar_cadera")
        return
        

    for desplazamiento_cadera in np.arange(-0.0, -6.6, -1.5):
        _ , (theta1, theta2) = bajar_cadera(leg, desplazamiento_cadera)
        if theta1 is None or theta2 is None:
            raise Exception("Error while calculating inverse kinematics in loop_bajar_cadera")
        if not setPosAngle(ser, leg, theta=(theta1, theta2)):
            raise Exception("Error while setting position in loop_bajar_cadera")
        await asyncio.sleep(1)
        
async def switch_state(queueAudio):
    """
    Checks if the queueAudio is not empty and if the incoming message is equal to MESSAGE_AUDIO.
    
    Parameters:
    - ser: The serial object.
    - leg: The leg object.
    - queueAudio: The queue containing audio messages.
    
    Returns:
    - True if the incoming message is equal to MESSAGE_AUDIO and the queueAudio is not empty.
    - False otherwise.
    """
    if not queueAudio.empty():
        incoming_message = await queueAudio.get()
        if incoming_message == MESSAGE_AUDIO:
            
            return True
    return False

async def move_robot_with_imbalance(ser, queue):
    """
    Moves the robot with imbalance using the given serial connection and queue.

    Parameters:
    ser (Serial): The serial connection to the robot.
    queue (tuple): A tuple containing two queues - queueWalk and queueAudio.

    Returns:
    None
    """
    if not isinstance(queue, tuple):
        return 
    queueWalk, queueAudio = queue

    leg = DERECHA
    state = MotionState.PASO0

    while True:
        #estado avanzar una pierna hacia delante
        if state == MotionState.PASO0:
            
            #comprobar si hay un mensaje de audio en la cola para cambiar de estado
            if await switch_state(queueAudio):
                print("FIN WALK")
                return

            #bajar cadera
            other_leg = switch_leg(leg)
            await loop_bajar_cadera(ser, other_leg, release=True)
            
            await asyncio.sleep(TIME_SLEEP)

            #mover pierna hacia delante rapidamente
            if not setPosAngle(ser, leg, theta=(WALK[0][0], WALK[0][1])):
                raise Exception("Error while setting position")
            
            print("PASO0 establecido (bajar cadera y avanzar pierna contraria una pierna)")
            
            await asyncio.sleep(TIME_SLEEP)
            
            state = MotionState.PASO1  # Pasar al siguiente estado
            
        #estado avanzar pierna contraria hacia delante
        elif state == MotionState.PASO1:
            
            if not setPosAngle(ser, other_leg, theta=(WALK[1][0], WALK[1][1])):
                raise Exception("Error while setting position")            
            
            await asyncio.sleep(TIME_SLEEP)
            #mover pierna contraria hacia delante rapidamente
            if not setPosAngle(ser, other_leg, theta=(WALK[0][0], WALK[0][1])):
                raise Exception("Error while setting position")
            
            print("PASO1 establecido (avanzar una pierna))")
            
            await asyncio.sleep(TIME_SLEEP)
            
            state = MotionState.PASO2  # Pasar al siguiente estado

        #levantar las dos patas 
        elif state == MotionState.PASO2:
            
            #pasos para elevar las dos piernas a la vez 
            if not await standup(ser):
                raise Exception("Error while standup position")
            
            print("STANDUP establecido")
            
            await asyncio.sleep(TIME_SLEEP)
            
            leg = other_leg
            state = MotionState.PASO0  # Pasar al siguiente estado

        else:
            raise Exception("Invalid state")

async def rotate_90_degrees(ser):
    """
    Moves the robot 90 degrees to the right using the given serial connection and queue.

    Parameters:
    ser (Serial): The serial connection to the robot.
    queue (tuple): A tuple containing two queues - queueGiro and queueAudio.

    Returns:
    None
    """

    leg = DERECHA
    state = MotionState.PASO0
    tiempo = time.time

    while True:
        #estado avanzar una pierna hacia delante

        if state == MotionState.PASO0:

            other_leg = switch_leg(leg)
            await loop_bajar_cadera(ser, other_leg, release=True)

            print(f"PASO 0 establecido (bajar cadera)")
            await asyncio.sleep(1)
            state = MotionState.PASO1

        if state == MotionState.PASO1:            
            print("GIRO 90")

            #mover pierna hacia delante rapidamente
            if not setPosAngle(ser, leg, theta=(WALK[0][0], WALK[0][1])):
                raise Exception("Error while setting position")
            #mover pierna hacia delante rapidamente
            if not setPosAngle(ser, leg, theta=(WALK[1][0], WALK[1][1])):
                raise Exception("Error while setting position")

            print(f"PASO 1 establecido (avanzar pierna contraria una pierna)")
            await asyncio.sleep(1)

            time_step1 = time.time

            # Pasar al siguiente estado
            if (time - time_step1 > 20):
                state = MotionState.PASO2

        #levantar las dos patas 
        elif state == MotionState.PASO2:
            
            #pasos para elevar las dos piernas a la vez 
            if not await standup(ser):
                raise Exception("Error while standup position")
            
            print("STANDUP establecido")
            await asyncio.sleep(0.5)
            return             
        else:
            raise Exception("Invalid state")


async def sit(ser):
    """
    Moves the servo motor to a sitting position.

    Args:
        ser (Serial): The serial connection to the servo motor.

    Returns:
        bool: True if the sitting position is successfully set, False otherwise.
    """
    
    for pos in COMANDOS_SIT:
        if not setPos(ser, pos):
            return False
        await asyncio.sleep(1)
    return True


async def standup(ser):
    """
    Moves the servo motor to different positions to make the robot stand up.

    Args:
        ser (Serial): The serial connection to the servo motor.

    Returns:
        bool: True if all positions are successfully set, False otherwise.
    """
    #    """
    for pos in COMANDOS_STANDUP:
        if not setPos(ser, pos):
            return False
        await asyncio.sleep(0.4)
    return True

async def rotate(ser,degrees):
    """ROTATE
    
    FALTA HACER ENTERO
    
    Args:
        degrees (int): degrees to rotate the robot
    """
    return True
    