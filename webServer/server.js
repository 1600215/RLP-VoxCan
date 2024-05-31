const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const https = require("https");

const app = express();
const port = 3000;

// Configuración de multer para guardar los archivos
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "./audio/");
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});
const upload = multer({ storage: storage });

app.use(express.static(path.join(__dirname, "public")));

app.post("/upload", upload.single("audio"), (req, res) => {
  res.sendStatus(200);
});

// Configuración del servidor HTTPS
const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

https.createServer(options, app).listen(port, () => {
  console.log(`Server running on port ${port}`);
});
