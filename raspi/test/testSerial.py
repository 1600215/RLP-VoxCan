import serial,time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.arduino import connect 

def testSerial(mode="pc"):
    """
    Connects to a serial device and returns True if the connection is successful.

    Parameters
    ----------
    mode : str, optional
        The mode of operation. Valid values are "pc" and "raspi". 
        Defaults to "pc".

    Returns
    -------
    bool
        True if the connection is successful, False otherwise.

    Raises
    ------
    None

    Notes
    -----
    This function connects to a serial device using the specified mode.
    It prints the connection status and attempts to establish a connection.
    If the connection is successful, it returns True. Otherwise, it returns False.

    Examples
    --------
    >>> testSerial("pc")
    Running. Press CTRL-C to exit.
    /dev/tty.usbserial-14130 connected!
    Intentando conectar...
    Tiempo de conexión:  0.123456789
    True

    >>> testSerial("raspi")
    Running. Press CTRL-C to exit.
    /dev/ttyUSB0 connected!
    Intentando conectar...
    Tiempo de conexión:  0.987654321
    True

    >>> testSerial("invalid")
    Modo no válido
    False
    """
    if mode == "pc":
        connection = "/dev/tty.usbserial-14130"
    elif mode == "raspi":
        connection = "/dev/ttyUSB0"
    else: 
        print("Modo no válido")
        return False
        
    print('Running. Press CTRL-C to exit.')
    with serial.Serial(connection, 9600, timeout=1) as ser:
        time.sleep(1) 
        if ser.isOpen():
            print("{} connected!".format(ser.port))
            try: 
                t0 = time.time()
                while not connect(ser): 
                    print("Intentando conectar...")
                    pass
                print("Tiempo de conexión: ", time.time()-t0)
                return True
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
                return False

if __name__ == '__main__':
    testSerial()