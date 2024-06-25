import serial,time
import sys, os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.arduino import connect 
from modules.motion import standup, sit

async def testInit(mode="pc"):

    if mode == "pc":
        connection = "/dev/tty.usbserial-14130"
    elif mode == "raspi":
        connection = "/dev/ttyUSB0"
    else: 
        print("Modo no válido")
        return False
        
    print('Running. Press CTRL-C to exit.')
    with serial.Serial(connection, 9600, timeout=1) as ser:
        await asyncio.sleep(1) 
        if ser.isOpen():
            print("{} connected!".format(ser.port))
            try: 
                t0 = time.time()
                while not connect(ser): 
                    print("Intentando conectar...")
                    pass
                print("Tiempo de conexión: ", time.time()-t0)
                
                if not await standup(ser):
                    raise Exception("Error al levantarse")
                
                await asyncio.sleep(3)
                
                print("Sending SIT")
            
                if not await sit(ser):
                    raise Exception("Error al sentarse")
                
                print("LEVANTADO Y SENTADO")
                
                await asyncio.sleep(3)
                
                if not await standup(ser):
                    raise Exception("Error al levantarse")

                print("LEVANTADO, SENTADO Y LEVANTADO")

            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
                return False

if __name__ == '__main__':
    asyncio.run(testInit())