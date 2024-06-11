import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.motion import calibrate_servo
from modules.calibrate import calibrate_servos
from modules.positions import setPos, getPos
from constants import  Axis

def calibrate_robot(ser, mpu, calibration):
    try:
        standby_params = calibrate_servos(ser, mpu)
        if standby_params is None:
            raise Exception("Error al calibrar los servos")
        set = setPos(ser, standby_params)
        if not set:
            raise Exception("Error al enviar los parámetros de calibración, durante estado calibración")
        calibration = calibrate_servo(Axis.DERECHO_SUP, 175, standby_params[Axis.DERECHO_SUP], calibration)
        calibration = calibrate_servo(Axis.DERECHO_INF, 100, standby_params[Axis.DERECHO_INF], calibration)
        calibration = calibrate_servo(Axis.IZQUIERDO_SUP, 175, standby_params[Axis.IZQUIERDO_SUP], calibration)
        calibration = calibrate_servo(Axis.IZQUIERDO_INF, 100, standby_params[Axis.IZQUIERDO_INF], calibration)
    except Exception as e:
        raise Exception("Error al calibrar los servos, estado CALIBRACIÓN", e)

    print("Calibración de los servos realizada con éxito")