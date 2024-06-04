const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const ffmpeg = require('fluent-ffmpeg');
const ffmpegPath = require('@ffmpeg-installer/ffmpeg').path;

ffmpeg.setFfmpegPath(ffmpegPath);

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Middleware para el cuerpo de la solicitud
app.use(express.json());
app.use(express.urlencoded({ extended: true }));



const port = 3000;

let command = null;


// Create uploads folder if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir);
}

// Configuration for multer to store audio files
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadsDir);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

// Dictionary to store usernames and associated files
let tokenFiles = {};

// Socket connections handling
io.on('connection', (socket) => {
    console.log('A user connected');

    if (command) {
        socket.emit('OnCommand', command);
    }

    socket.on('check-token', (token) => {
        const exists = !!tokenFiles[token];
        socket.emit('token-exists', exists);
    });

    socket.on('disconnect', () => {
        console.log('User disconnected');
    });

});

// Endpoint to handle audio file uploads
app.post('/upload', upload.single('audio'), (req, res) => {
    const name = req.body.name;

    if (!userFiles[name]) {
        return res.status(401).send('Invalid name');
    }

    if (req.file) {

        const fileName = `${Date.now()}.mp3`
        const inputFilePath = path.join(uploadsDir, req.file.filename);
        const outputFilePath = path.join(uploadsDir, fileName);

        ffmpeg(inputFilePath)
            .toFormat('mp3')
            .on('end', () => {
                fs.unlinkSync(inputFilePath); // Remove original .webm file
                userFiles[name].push(fileName);
                console.log(`Audio file uploaded and converted with name: ${name} , file: ${fileName}`);
                res.status(200).send(outputFilePath); // Send the file name as response
            })
            .on('error', (err) => {
                console.error('Error converting file:', err);
                res.status(500).send('Failed to convert file');
            })
            .save(outputFilePath);
    } else {
        res.status(400).send('Failed to upload file');
    }
});


app.post('/set-command', (req, res) => {
    const  filename  = req.body.filename;

    let usuarioEncontrado = null;
    for (const token in tokenFiles) {
        if (tokenFiles[token].includes(filename)) {
            usuarioEncontrado = token;
            break;
        }
    }

    if (usuarioEncontrado) {
        command = usuarioEncontrado;
        io.emit('CommandAccepted', usuarioEncontrado)
        res.status(200).send(`El archivo '${filename}' pertenece al usuario '${usuarioEncontrado}'.`);
    } else {
        res.status(200).send(`No se encontró ningún usuario asociado al archivo '${filename}'.`);
    }
});

app.post('/finish-command', (req, res) => {
    command = null;
    io.emit('commandFinished');
    res.status(200).send('Comando finalizado.');
});

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Serve HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

server.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
