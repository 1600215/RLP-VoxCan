import serial
import time
import json
import math
import mpu6050


# Direccion del MPU6050 
MPU6050_ADDR = 0x68


#-----------------------------------------------------------------------
#Estados de nuestra maquina de estados del robot VOXCAN
class State:
    INITIALIZE = 0
    CONNECTING = 1
    CALIBRATION = 2
    STANDBY = 3
    COMMAND = 4


#-----------------------------------------------------------------------
# Inicialización del puerto serie
try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
except serial.SerialException as e:
    print("Error de comunicación serial con Arduino Nano:", e)


#-----------------------------------------------------------------------
#Inicialización del MPU6050
try:
    mpu = mpu6050.mpu6050(MPU6050_ADDR)
    
except Exception as e:
    print("Error al inicializar el MPU6050:", e)
current_state = State.CALIBRATION



#-----------------------------------------------------------------------
#Función para caluclar el desbalanceo en los ejes x y y

def calcular_desbalanceo():
    # Leer datos del acelerómetro y el giroscopio
    acelerometro = mpu.get_accel_data()

    # Calcular ángulo de inclinación en cada eje a partir del acelerómetro
    inclinacion_x = math.atan2(acelerometro['y'], acelerometro['z']) * 180 / math.pi
    inclinacion_y = math.atan2(-acelerometro['x'], math.sqrt(acelerometro['y']**2 + acelerometro['z']**2)) * 180 / math.pi


    # Devolver desbalanceo en ambos ejes
    return inclinacion_x, inclinacion_y


#-----------------------------------------------------------------------
#Bucle principal de la Raspberry Pi


while True:
    try: 
    
        #-----------------------------------------------------------------------
        #Estado inicial para realizar conexión con el arduino nano
        if current_state == State.INITIALIZE:
            #si la conexión con el Arduino Nano está abierta
            if ser.isOpen():
                print("Arduino Nano conectado")
                # Enviar el comando de conexión al Arduino
                try:
                    res = {"command" : "CONNECT"}
                    ser.write(json.dumps(res).encode() + b'\n')
                    current_state = State.CONNECTING
                except Exception as e:
                    print("Error al enviar el comando de conexión:", e)
            
        #-----------------------------------------------------------------------
        #Estado de conexión con el arduino nano
        elif current_state == State.CONNECTING:
            # Esperar la respuesta del Arduino
            if ser.in_waiting > 0:
                recv = ser.readline().decode().strip()
                recv = json.loads(recv)
                if "status" in recv and recv["status"] == "CONNECTED":
                    print("Arduino Nano conectado")
                    current_state = State.CALIBRATION

        #-----------------------------------------------------------------------
        #Calibración de los servos de nuestro robot VOXCAN
        elif current_state == State.CALIBRATION:
            
                        
            #min = DBL_MAX
            config = None
            while True:      
                          
                #Comprueba si esta desequilibrado
                ser.write(json.dumps({"command" : "getPos"}).encode() + b'\n')
                while ser.in_waiting == 0:
                    pass
                recv = json.loads(ser.readline().decode().strip())
                print(recv)
                
                #Si no esta desequilibrado devuelve {status : "BALANCED"}
                
                
                #Si esta desequilibrado devuelve {status : "UNBALANCED"}


            current_state = State.STANDBY
            
        #-----------------------------------------------------------------------    
        elif current_state == State.STANDBY:
            print("Esperando comando desde la Raspberry Pi...")

            current_state = State.COMMAND
            
        #-----------------------------------------------------------------------
        elif current_state == State.COMMAND:
            # Esperar la respuesta del Arduino (opcional)
            response = ser.readline().decode().strip()
            print("Respuesta del Arduino:", response)
            # Volver al estado de espera
            current_state = State.STANDBY
            
        #-----------------------------------------------------------------------
        else:
            print("Error")

    except Exception as e:
        print("Error en el bucle funcional:", e)
