import serial,time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.connect import connect 
from modules.positions import getPos, setPos
from constants import Axis

def testPositions(mode="pc"):
    """
    Test the positions of a device connected via serial communication.

    Parameters:
    - mode (str): The mode of connection. Valid values are "pc" and "raspi". Default is "pc".

    Returns:
    - bool: True if the test is successful, False otherwise.
    """

    print('Running. Press CTRL-C to exit.')

    # Test connecting via serial to the PC
    if mode == "pc":
        conection = "/dev/tty.usbserial-14130"
    elif mode == "raspi":
        conection = "/dev/ttyUSB0"
    else:
        print("Invalid mode")
        return False

    with serial.Serial(conection, 9600, timeout=1) as ser:
        time.sleep(1)
        if ser.isOpen():
            print("{} connected!".format(ser.port))
            try:
                t0 = time.time()
                while not connect(ser):
                    print("Trying to connect...")
                    pass
                i = 0
                while i < 180:
                    print("Connection time: ", time.time() - t0)
                    _ = setPos(ser, {str(Axis.DERECHO_SUP): i})
                    time.sleep(1)
                    print("Sending {'command': Command.GET_POS} to Arduino")
                    print("Received: ", getPos(ser))
                    i = i + 10

            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
                return False

if __name__ == '__main__':
    testPositions()