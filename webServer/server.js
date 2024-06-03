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

const port = 3000;

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
let userFiles = {};

// Socket connections handling
io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('submit-name', (name) => {
        if (!userFiles[name]) {
            userFiles[name] = [];
        }
        socket.emit('name-accepted', true);
    });

    socket.on('check-name', (name) => {
        const exists = !!userFiles[name];
        socket.emit('name-exists', exists);
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
        const inputFilePath = path.join(uploadsDir, req.file.filename);
        const outputFilePath = path.join(uploadsDir, `${Date.now()}.mp3`);

        ffmpeg(inputFilePath)
            .toFormat('mp3')
            .on('end', () => {
                fs.unlinkSync(inputFilePath); // Remove original .webm file
                userFiles[name].push(outputFilePath);
                console.log(`Audio file uploaded and converted with name: ${name}`);
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
