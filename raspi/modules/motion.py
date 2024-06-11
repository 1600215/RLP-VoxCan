import os, sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import Axis, l1, l2, DERECHA, IZQUIERDA


# Función de calibración
def calibrate_servo(servo_name, joint_angle_ref, servo_angle_ref, calibrations):
    """
    Calibrates a servo by storing the joint angle reference and servo angle reference in the calibrations dictionary.

    Args:
        servo_name (str): The name of the servo.
        joint_angle_ref (float): The reference angle of the joint.
        servo_angle_ref (float): The reference angle of the servo.
        calibrations (dict): The dictionary containing the servo calibrations.

    Returns:
        dict: The updated calibrations dictionary.
    """
    calibrations[servo_name] = {
        'joint_angle_ref': joint_angle_ref,
        'servo_angle_ref': servo_angle_ref,
    }
    return calibrations

# Función de mapeo de ángulos
def map_angle_to_servo(servo_name, joint_angle, calibrations):
    """
    Maps the joint angle to the corresponding servo angle based on the given servo name and calibrations.

    Args:
        servo_name (str): The name of the servo.
        joint_angle (float): The joint angle to be mapped.
        calibrations (dict): The calibration values for the servos.

    Returns:
        float: The mapped servo angle.

    Raises:
        None

    """
    calib = calibrations[servo_name]
    
    if Axis.DERECHO_SUP == servo_name:
        servo_angle = (calib['joint_angle_ref'] - joint_angle) + calib['servo_angle_ref']
    elif Axis.DERECHO_INF == servo_name:
        servo_angle = (calib['joint_angle_ref'] - joint_angle) + calib['servo_angle_ref']
    elif Axis.IZQUIERDO_SUP == servo_name:
        servo_angle = (joint_angle - calib['joint_angle_ref']) + calib['servo_angle_ref']
    elif Axis.IZQUIERDO_INF == servo_name:
        servo_angle = (joint_angle - calib['joint_angle_ref']) + calib['servo_angle_ref']
    else:
        return None
    
    if servo_angle < 0 or servo_angle > 180:
        return None
    return servo_angle

# Función de mapeo de servo a ángulo
def map_servo_to_angle(servo_name, servo_angle, calibrations):
    """
    Maps the servo angle to the corresponding joint angle based on the given calibrations.

    Args:
        servo_name (str): The name of the servo.
        servo_angle (float): The angle of the servo in degrees.
        calibrations (dict): The calibration values for each servo.

    Returns:
        float: The corresponding joint angle in degrees, or None if the servo angle is out of range.
    """
    if servo_angle < 0 or servo_angle > 180:
        return None
    
    calib = calibrations[servo_name]
    
    if Axis.DERECHO_SUP == servo_name:
        joint_angle = calib['joint_angle_ref'] + (calib['servo_angle_ref'] - servo_angle)
    elif Axis.DERECHO_INF == servo_name:
        joint_angle = calib['joint_angle_ref'] + (calib['servo_angle_ref'] - servo_angle)
    elif Axis.IZQUIERDO_SUP == servo_name:
        joint_angle = (servo_angle - calib['servo_angle_ref']) + calib['joint_angle_ref']
    elif Axis.IZQUIERDO_INF == servo_name:
        joint_angle = (servo_angle - calib['servo_angle_ref']) + calib['joint_angle_ref']
    else:
        return None

    return joint_angle


def cinematica_directa(theta1, theta2):
    """
    Calculates the forward kinematics of a robotic arm given the joint angles.

    Parameters:
    theta1 (float): Angle of the first joint in degrees.
    theta2 (float): Angle of the second joint in degrees.

    Returns:
    tuple: A tuple containing two tuples. The first tuple represents the coordinates of the knee joint (x_rodilla, y_rodilla),
        and the second tuple represents the coordinates of the foot joint (x_pie, y_pie).
    """
    x_rodilla = l1 * np.cos(np.radians(theta1))
    y_rodilla = l1 * np.sin(np.radians(theta1))
    
    x_pie = x_rodilla + l2 * np.cos(np.radians(theta1 + theta2))
    y_pie = y_rodilla + l2 * np.sin(np.radians(theta1 + theta2))
    
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
    beta = np.arccos((l1**2 + d**2 - l2**2) / (2 * l1 * d))
    
    theta1 = np.degrees(alpha - beta)
    theta2 = np.degrees(np.arccos((l1**2 + l2**2 - d**2) / (2 * l1 * l2))) - 180
    
    return theta1, theta2


def bajar_cadera(type, servo1, servo2, desplazamiento_vertical, calibrations):
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
        theta1_inicial = map_servo_to_angle(Axis.DERECHO_SUP, servo1, calibrations)
        theta2_inicial = map_servo_to_angle(Axis.DERECHO_INF, servo2, calibrations)
    elif type == IZQUIERDA:
        theta1_inicial = map_servo_to_angle(Axis.IZQUIERDO_SUP, servo1, calibrations)
        theta2_inicial = map_servo_to_angle(Axis.IZQUIERDO_INF, servo2, calibrations)
    else:
        return None
    
    _, (x_pie, y_pie) = cinematica_directa(theta1_inicial, theta2_inicial)
    
    theta1_new, theta2_new = cinematica_inversa(x_pie, y_pie, desplazamiento_vertical)
    theta2_new = np.abs(theta2_new)
    
    if (theta1_new < 0):
        theta1_new = theta1_new + 360
    
    (rodilla_x, rodilla_y), _ = cinematica_directa(theta1_new, theta2_new)
    return (rodilla_x, rodilla_y), (theta1_new, theta2_new)