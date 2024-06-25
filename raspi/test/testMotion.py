import sys, os 
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.motion import calibrate_servo, map_angle_to_servo, map_servo_to_angle, bajar_cadera
from constants import Axis, DERECHA, IZQUIERDA


calibrations = {}
calibrate_servo(Axis.IZQUIERDO_SUP, 185, 30, calibrations)
calibrate_servo(Axis.IZQUIERDO_INF, 100, 135, calibrations)
calibrate_servo(Axis.DERECHO_SUP, 185, 150, calibrations)
calibrate_servo(Axis.DERECHO_INF, 100, 45, calibrations)
 


# Función de prueba para map_angle_to_servo
def test_map_angle_to_servo():
    
    # Testing map_angle_to_servo
    assert map_angle_to_servo(Axis.IZQUIERDO_SUP, 175, calibrations) == 20
    assert map_angle_to_servo(Axis.IZQUIERDO_INF, 100, calibrations) == 135
    assert map_angle_to_servo(Axis.DERECHO_SUP, 175, calibrations) == 160
    assert map_angle_to_servo(Axis.DERECHO_INF, 100, calibrations) == 45
    assert map_angle_to_servo(Axis.DERECHO_SUP, 120, calibrations) == None

    print("test_map_angle_to_servo passed")

# Función de prueba para map_servo_to_angle
def test_map_servo_to_angle():

    # Testing map_servo_to_angle
    assert map_servo_to_angle(Axis.IZQUIERDO_SUP, 20, calibrations) == 175
    assert map_servo_to_angle(Axis.IZQUIERDO_INF, 135, calibrations) == 100
    assert map_servo_to_angle(Axis.DERECHO_SUP, 160, calibrations) == 175
    assert map_servo_to_angle(Axis.DERECHO_INF, 45, calibrations) == 100
    assert map_servo_to_angle(Axis.DERECHO_INF, 200, calibrations) == None

    print("test_map_servo_to_angle passed")


def test_bajar_cadera():
    # Caso de prueba 1: Tipo DERECHA
    type = DERECHA
    servo1 = 150
    servo2 = 45
    desplazamiento_vertical = -1.0
    rodilla_pos, (theta1_new, theta2_new) = bajar_cadera(type, servo1, servo2, desplazamiento_vertical, calibrations)
    assert np.isclose(rodilla_pos[1], -0.19, atol=0.01)
    assert np.isclose(rodilla_pos[0], -13.5, atol=0.01)
    assert np.isclose(theta1_new, 180.81, atol=0.01)
    assert np.isclose(theta2_new, 104.37, atol=0.01)
    
    # Caso de prueba 2: Tipo IZQUIERDA
    type = IZQUIERDA
    servo1 = 30
    servo2 = 135
    desplazamiento_vertical = -0.5
    rodilla_pos, (theta1_new, theta2_new) = bajar_cadera(type, servo1, servo2, desplazamiento_vertical, calibrations)
    assert np.isclose(rodilla_pos[0],-13.48, atol=0.01)
    assert np.isclose(rodilla_pos[1],-0.69, atol=0.01)
    assert np.isclose(theta1_new, 182.91, atol=0.01)    
    assert np.isclose(theta2_new, 102.21, atol=0.01)
    
    print("Pruebas de bajar_cadera completadas")


if __name__ == "__main__":
    test_map_angle_to_servo()
    test_map_servo_to_angle()
    test_bajar_cadera()
    
    print("All tests passed")