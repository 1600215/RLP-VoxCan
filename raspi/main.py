import serial
import time
import mpu6050

#direccion del MPU6050 
MPU6050_ADDR = 0x68

class State:
    STANDBY = 0
    COMMAND = 1 
    


## Inicialización puerto serie 
try:
    ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
except serial.SerialException as e:
    print("Error comunicación serial con arduino nano", e)

current_state = State.STANDBY


while True:

    try: 
        if current_state == State.STANDBY:
            print("robot esperando")
            #mirar por el puerto serie si viene algún comando de voz, si viene analizarlo -> TIRAR comanda en caso afirmativo (current_state = State.COMMAND)
            #if condition to command :
                #current_state = State.COMMAND
            #elif other possible state 
    
        elif current_state == State.COMMAND:
            print("haciendo comanda")
            #if command finished:
                #current_State = State.COMMAND
            #elif or else
                #other possible states or stay here

            #aquí vendria el control de la posicion del robot, utilizar funciones de mover, mantener el equilibrio etc
        else:
            print("error")
    except Exception as e:
        print("error bucle funcional ", e)


    
