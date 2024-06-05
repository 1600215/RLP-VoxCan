import serial,time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.connect import connect 

def testSerial(mode="pc"):
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