import serial
import time
import numpy as np
import sys
from main import Command, Axis, getPos, setPos


try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    time.sleep(1)
except serial.serialutil.SerialException:
    print("Serial port not found")
    sys.exit(1)


def testSerial():
    print("Testing serial communication with Arduino")
    print("Sending {'command' : Command.SET_POS, 'parametros' : {'0' : 45, '1' : 50} to Arduino")
    
    for i, j in np.arange(0, 180, 10), np.arange(180, 0, 10):
        _ , _ = setPos(ser, {str(Axis.DERECHO_SUP): i, str(Axis.DERECHO_INF) : j})
        time.sleep(1)
        print("Sending {'command' : Command.GET_POS} to Arduino")
        pos = getPos(ser)
        print("Received: ", pos)
        
        if pos != {str(Axis.DERECHO_SUP): i, str(Axis.DERECHO_INF) : j}:
            print("Test failed in", i, j)
            return False
    print("Test passed")
    return True
    

    