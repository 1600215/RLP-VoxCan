import math

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

