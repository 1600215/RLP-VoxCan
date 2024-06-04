// multi_client.js

const io = require('socket.io-client');

const clientCount = 3;  // Número de clientes a crear
const clients = [];

for (let i = 0; i < clientCount; i++) {
    const socket = io('http://localhost:3000');
    clients.push(socket);

    socket.on('connect', () => {
        console.log(`Client ${i} connected to server`);

        // Simular envío de nombre de usuario
        const userName = `testuser${i}`;
        socket.emit('submit-name', userName);

        socket.on('name-accepted', (accepted) => {
            if (accepted) {
                console.log(`Client ${i} name accepted: ${userName}`);
            }
        });

        socket.on('name-exists', (exists) => {
            console.log(`Client ${i} name exists: ${exists}`);
        });

        socket.on('command', (command) => {
            console.log(`Client ${i} command received: ${command}`);
        });
    });

    socket.on('disconnect', () => {
        console.log(`Client ${i} disconnected from server`);
    });
}
