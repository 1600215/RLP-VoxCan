import serial,time
import sys, os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.connect import connect 
from modules.positions import getPos, setPos
from constants import Axis

def testPositions():    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/tty.usbserial-14130", 9600, timeout=1) as ser:
        time.sleep(1) 
        if ser.isOpen():
            print("{} connected!".format(ser.port))
            try: 
                t0 = time.time()
                while not connect(ser): 
                    print("Intentando conectar...")
                    pass
                i= 0
                while i < 180:
                    print("Tiempo de conexión: ", time.time()-t0)
                    _= setPos(ser, {str(Axis.DERECHO_SUP): i})
                    time.sleep(1)
                    print("Sending {'command' : Command.GET_POS} to Arduino")
                    print("Received: ", getPos(ser))
                    i = i + 10
                    
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
                return False

if __name__ == '__main__':
    testPositions()