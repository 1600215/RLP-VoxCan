document.addEventListener("DOMContentLoaded", () => {
  let mediaRecorder; // Controla la grabación de medios
  let audioChunks = []; // Almacena fragmentos de audio grabados
  const recordButton = document.getElementById("recordButton"); // Referencia al botón de grabación
  const textSection = document.getElementById("msg"); // Referencia al elemento de mensaje dinámico

  let recording = false; // Indica si la grabación está en curso
  let token; // Token único para identificar al usuario
  let command = null; // Comando actual del usuario

  const socket = io(); // Inicializa la conexión con Socket.io

  // Verifica si hay un token guardado en localStorage
  const savedToken = localStorage.getItem('token');
  if (savedToken) {
      token = savedToken;
      recordButton.disabled = true; // Deshabilita el botón de grabación
      socket.emit('check-token', token); // Envía el token al servidor para verificación
      console.log("check-token", token);
  } else {
      token = uuid.v4(); // Genera un nuevo token
      localStorage.setItem('token', token); // Guarda el token en localStorage
      socket.emit('submit-token', token); // Envía el nuevo token al servidor
      console.log("submit token ",token);
  }

  // Maneja los datos de audio disponibles
  const handleDataAvailable = (event) => {
      audioChunks.push(event.data);
  };

  // Maneja la detención de la grabación y sube el archivo al servidor
  const handleStop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      audioChunks = [];
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("token", token);

      try {
          const response = await fetch("/upload", {
              method: "POST",
              body: formData,
          });
          if (response.ok) {
              alert("Audio uploaded and converted to MP3 successfully!");
          } else {
              alert("Failed to upload audio");
          }
      } catch (error) {
          console.error("Error uploading audio:", error);
          alert("Error uploading audio");
      }
  };

  // Inicia la grabación de audio, cambia el botón a "Stop Recording" y cambia el estilo del botón
  const startRecording = async () => {
      try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = handleDataAvailable;
          mediaRecorder.onstop = handleStop;
          mediaRecorder.start();
          recordButton.textContent = "Stop Recording";
          recordButton.classList.add("stop-recording"); // Cambia el color del botón a rojo
          recording = true;
      } catch (error) {
          console.error("Error accessing media devices:", error);
          alert("Error accessing media devices");
      }
  };

  // Detiene la grabación de audio, cambia el botón a "Start Recording" y restaura el estilo del botón
  const stopRecording = () => {
      mediaRecorder.stop();
      recordButton.textContent = "Start Recording";
      recordButton.classList.remove("stop-recording"); // Restaura el color del botón a verde
      recording = false;
  };

  // Alterna entre iniciar y detener la grabación al hacer clic en el botón
  recordButton.addEventListener("click", () => {
      if (!recording) {
          startRecording();
      } else {
          stopRecording();
      }
  });

  // Gestiona los comandos aceptados, muestra mensajes y deshabilita el botón de grabación
  socket.on("CommandAccepted", ({userToken, person, text}) => {
    command = userToken;
    console.log("CommandAccepted", userToken, token);
    textSection.textContent = text;
    if (token === userToken) {
        alert("Robot is now being used by you");
        textSection.style.color = "green";
    } else {
        alert("Robot is being used by user " + person);
        textSection.style.color = "red";
    }
    recordButton.disabled = true; 
  });

  // Gestiona los comandos en curso, muestra mensajes y deshabilita el botón de grabación
  socket.on("OnCommand", ({userToken, person, text}) => {
    command = userToken;
    console.log("OnCommand", userToken, token);

    textSection.textContent = text;
    if (token === userToken) {
        alert("Robot is now being used by you");
        textSection.style.color = "green";
    } else {
        alert("Robot is being used by user " + person);
        textSection.style.color = "red";
    }
    recordButton.disabled = true; 
  });

  // Indica que el comando ha finalizado, habilita el botón de grabación y limpia el mensaje
  socket.on("commandFinished", () => {
    command = null;
    alert("Robot is now available");
    recordButton.disabled = false;
    textSection.textContent = "";
  });

  // Habilita el botón de grabación si el token es aceptado
  socket.on("token-accepted", () => {
      recordButton.disabled = false;
  });

  // Gestiona la existencia del token, deshabilitando el botón si hay un comando en curso
  socket.on("token-exists", (exists) => {
      if (exists) {
          if (command) {
              recordButton.disabled = true;
          } else {
              recordButton.disabled = false;
          }
      } else {
          token = uuid.v4(); // Genera un nuevo token si el existente no es válido
          localStorage.setItem('token', token); // Guarda el nuevo token en localStorage
          socket.emit('submit-token', token); // Envía el nuevo token al servidor
          recordButton.disabled = true;
      }
  });
});
