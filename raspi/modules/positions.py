from constants import Command, Status
import json

#-----------------------------------------------------------------------
#Función para obtener la posición de los servos

def getPos(ser):
    '''The `getPos` function sends a command to a serial device to retrieve position data and returns the
    initial position received.
    
    Returns
    -------
        The `getPos()` function returns the initial position received from the serial port after sending a
    command to get the position.
    
    {"0" : 90, "1" : 90, "2" : 90, "3" : 90, "4" : 90}
    
    '''
    
    
    command = {'command': Command.GET_POS}
    ser.write((json.dumps(command) + '\n').encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    try:
        initialPos = json.loads(ser.readline().decode().rstrip())
    except:
        
        print("Error al cargar el json")
        return None
    
    if "status" in initialPos and initialPos["status"] == Status.OK:
        return initialPos['positions']
    
    return None         

#-----------------------------------------------------------------------
#Función para enviar los parámetros de los servos

def setPos(ser, params):
    """
    Sets the position of the servo motor.

    Args:
        ser (Serial): The serial connection to the servo motor.
        params (dict): The parameters for setting the position.

    Returns:
        bool: True if the position was set successfully, False otherwise.
    """
    command = {'command': Command.SET_POS, 'parametros': params}
    
    ser.write((json.dumps(command)+ '\n').encode('utf-8'))
    ser.flush()
                
    while ser.in_waiting == 0:
        pass
    
    recv = json.loads(ser.readline().decode().rstrip())
    print(recv)
    if(recv["status"] == Status.OK):
        return True
    
    return False