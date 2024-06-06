const io = require("socket.io-client");
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { v4: uuid } = require('uuid');
const FormData = require('form-data');

const clientCount = 3;  // Número de clientes a crear
const clients = [];
const uploadIntervals = {};

async function uploadFile(userId, token) {
    try {
        const filePath = path.join(__dirname, 'aux.mp3'); // Cambia esto a un archivo de audio válido en tu sistema
        const formData = new FormData();
        formData.append('audio', fs.createReadStream(filePath));
        formData.append('token', token);

        const response = await axios.post('localhost:3000/upload', formData, {
            headers: formData.getHeaders(),
        });
    } catch (error) {
        console.error(`User ${userId} failed to upload file:`, error.message);
    }
}

for (let i = 0; i < clientCount; i++) {
    const socket = io('https://localhost:3000');
    const userId = i;
    let token;

    clients.push(socket);

    socket.on('connect', () => {
        console.log(`Client ${userId} connected to server`);

        token = uuid();
        socket.emit('submit-token', token);

        socket.on('token-accepted', () => {
            console.log(`Client ${userId} name accepted: ${token}`);

            uploadIntervals[userId] = setInterval(() =>{
                 uploadFile(userId, token);
            }, 20000);
        });

        socket.on('token-exists', (exists) => {
            console.log(`Client ${userId} name exists: ${exists}`);
        });

        socket.on('CommandAccepted', (data) => {
            console.log(`Client ${userId} received CommandAccepted: ${data}`);
            clearInterval(uploadIntervals[userId]);

        });

        socket.on('commandFinished', () => {
            console.log(`Client ${userId} received commandFinished`);
            uploadIntervals[userId] = setInterval(() => uploadFile(userId, token), 3000);
        });
    });

    socket.on('disconnect', () => {
        console.log(`Client ${userId} disconnected from server`);
    });

}
