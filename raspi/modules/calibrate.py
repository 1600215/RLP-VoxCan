import sys
import numpy as np
from constants import Axis
from modules.positions import getPos, setPos
from modules.accel import calcular_desbalanceo

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
                        if setPos(ser,  {str(Axis.DERECHO_SUP) : angulo_eje_1, str(Axis.DERECHO_INF) : angulo_eje_2, str(Axis.IZQUIERDO_SUP) : angulo_eje_3, str(Axis.IZQUIERDO_INF) : angulo_eje_4}):
                            incl_x, incl_y = calcular_desbalanceo(mpu)
                        
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

