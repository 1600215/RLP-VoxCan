import asyncio

# Definimos un mensaje estándar
class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

# Función asincrónica de un peer
async def peer(name, queues):
    send_queue, recv_queue = queues
    while True:
        # Enviar un mensaje
        message = Message(sender=name, content=f"Hello from {name}")
        await send_queue.put(message)
        print(f"{name} sent: {message.content}")

        # Comprobar si hay un mensaje en la cola sin bloquear
        if not recv_queue.empty():
            incoming_message = await recv_queue.get()
            print(f"{name} received: {incoming_message.content} from {incoming_message.sender}")
        else:
            print(f"{name} did not receive any message")

        await asyncio.sleep(1)

async def main():
    # Crear las colas
    queue1 = asyncio.Queue()
    queue2 = asyncio.Queue()

    # Crear y arrancar las tareas de los peers
    peer1_task = asyncio.create_task(peer("Peer1", (queue1, queue2)))
    peer2_task = asyncio.create_task(peer("Peer2", (queue2, queue1)))

    # Esperar que ambas tareas terminen (en este caso, corren indefinidamente)
    await asyncio.gather(peer1_task, peer2_task)

if __name__ == "__main__":
    asyncio.run(main())
