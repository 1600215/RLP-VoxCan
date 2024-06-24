import serial,time
import sys, os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.arduino import connect
from modules.motion import move_robot_with_imbalance, standup
from constants import MESSAGE_AUDIO


async def putMessageQueue(queueAudio):
    print("putMessageQueueAudio")
    await asyncio.sleep(15)
    await queueAudio.put(MESSAGE_AUDIO)

async def testWalk(mode="pc"):
    if mode == "pc":
        connection = "/dev/tty.usbserial-14130"
    elif mode == "raspi":
        connection = "/dev/ttyUSB0"
    else: 
        print("Modo no válido")
        return False
    

    queueWalk = asyncio.Queue()
    queueAudio = asyncio.Queue()

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
                
                #task to send message by the queueAudio
                
                await standup(ser)
                
                await asyncio.sleep(5)
                
                # Test move_robot_with_imbalance
                task = asyncio.create_task(move_robot_with_imbalance(ser, queue=(queueWalk, queueAudio)))
                await task
                
                print("ACABADO CAMINAR CAMBIA DE ESTADO")
                
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
                return False

if __name__ == '__main__':
    asyncio.run(testWalk())