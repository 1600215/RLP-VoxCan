from constants import Command, Status
import json 

#-----------------------------------------------------------------------
#Función para enviar el comando de conexión al arduino nano

def connect(ser):
    '''The `connect` function establishes communication with an Arduino Nano and returns True if
    successful, otherwise returns False.
    
    Returns
    -------
        The `connect()` function returns a boolean value - `True` if the communication with the Arduino
    Nano was successful and it is connected, and `False` if there was an error in communication or the
    connection was not successful.
    
    '''

    res = {'command' : Command.CONNECT}
    ser.write(json.dumps(res).encode('utf-8'))
    ser.flush()
                    
    while ser.in_waiting == 0:
        pass
                    
    recv = ser.readline().decode('utf-8').rstrip()
    
    
    try:
        recv = json.loads(recv)
    except:    
        print("Error al cargar el json - volvemos a intentar")
        return False
        
    if "status" in recv and recv["status"] == Status.OK:
        print("Arduino Nano comunicado")
        return True
                    
    print("Error al comunicar con el Arduino Nano - volvemos a intentar")
    return False
    