const express = require("express");
const https = require("https");
const { Server } = require("socket.io");
const multer = require("multer");
const path = require("path");
const fs = require("fs");

// Opciones para la configuración HTTPS
const options = {
  key: fs.readFileSync("certs/key.pem"),
  cert: fs.readFileSync("certs/cert.pem"),
  secureProtocol: "TLSv1_2_method", // Especifica la versión de SSL/TLS aquí
};

const app = express();
const server = https.createServer(options, app);
const io = new Server(server);

// Middleware para el cuerpo de la solicitud
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const port = 3000;


//token del usuario utilizando el robot
let token = null;
//persona utilizando el robot
let person = null;
//texto del comando
let text = null;
//numero de comanda
let command = null;
//indica si el comando ha finalizado
let finished = true;

// Crea la carpeta de cargas si no existe
const uploadsDir = path.join(__dirname, "../uploads");
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// Configuración de multer para almacenar archivos de audio
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});

const upload = multer({ storage: storage });

// Diccionario para almacenar tokens y archivos asociados
let tokenFiles = {};

// Manejo de conexiones de Socket.io
io.on("connection", (socket) => {
  console.log("A user connected");

  // Maneja la recepción de un nuevo token
  socket.on("submit-token", (userToken) => {
    tokenFiles[userToken] = [];
    socket.emit("token-accepted", { userToken: token, person, text, command });
  });

  // Verifica la existencia de un token
  socket.on("check-token", (token) => {
    const exists = !!tokenFiles[token];
    socket.emit("token-exists", exists);
  });

  socket.on("check-command", () => {
    socket.emit("is-command", { userToken: token, person, text, command, finished });
  });
  // Maneja la desconexión de un usuario
  socket.on("disconnect", () => {
    console.log("User disconnected");
  });
});

// Endpoint para manejar la subida de archivos de audio
app.post("/upload", upload.single("audio"), (req, res) => {
  const token = req.body.token;

  if (!tokenFiles[token]) {
    return res.status(401).send("Invalid token");
  }

  if (req.file) {
    const fileName = req.file.filename;
    tokenFiles[token].push(fileName);
    console.log(`Audio file uploaded with token: ${token}, file: ${fileName}`);
    res.status(200).send("Audio file uploaded successfully!");
  } else {
    res.status(400).send("Failed to upload file");
  }
});

// Endpoint para establecer un comando
app.post("/set-command", (req, res) => {
  const filename = req.body.filename;

  console.log(req.body);
  let usuarioEncontrado = null;
  for (const token in tokenFiles) {
    if (tokenFiles[token].includes(filename)) {
      usuarioEncontrado = token;
      break;
    }
  }

  if (usuarioEncontrado) {
    token = usuarioEncontrado;
    person = req.body.person;
    text = req.body.text;
    command = req.body.command;
    if(parseInt(command) !== 5) finished = false;
    io.emit("command-accepted", { userToken: usuarioEncontrado, person, text, command });
    res.status(200).send(`El archivo '${filename}' pertenece al usuario '${usuarioEncontrado}'.`);
  } else {
    res.status(200).send(`No se encontró ningún usuario asociado al archivo '${filename}'.`);
  }
});

// Endpoint para finalizar un comando
app.post("/go-standby", (req, res) => {
  token = null;
  person = null;
  text = null;
  command = null;
  finished = true;
  io.emit("go-standby");

  res.status(200).send("Comando finalizado.");
});


app.post('/finish-command', (req,res) =>{
  finished = true;
  io.emit("finish-command", {userToken: token});
  res.status(200).send("Comando finalizado.");
});

// Sirve archivos estáticos
app.use(express.static(path.join(__dirname, "public")));

// Sirve el archivo HTML principal
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Inicia el servidor
server.listen(port, () => {
  console.log(`Server is running at https://localhost:${port}`);
});
