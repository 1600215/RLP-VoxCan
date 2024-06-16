document.addEventListener("DOMContentLoaded", () => {
  let mediaRecorder; // Controla la grabación de medios
  let audioChunks = []; // Almacena fragmentos de audio grabados
  const recordButton = document.getElementById("recordButton"); // Referencia al botón de grabación
  const textSection = document.getElementById("msg"); // Referencia al elemento de mensaje dinámico
  const commandSection = document.getElementById("command"); // Referencia al elemento de comando dinámico

  let recording = false; // Indica si la grabación está en curso
  let token; // Token del cliente
  let commandToken = null; // token del usuario que tiene el robot utilizandolo

  const STANDBY = 3;
  const SIT = 4;
  const WALK = 5;
  const ROTATE = 7;
  const STANDUP = 8;

  const socket = io(); // Inicializa la conexión con Socket.io

  /**
   * Convierte el comando numérico a su representación en cadena.
   * @param {number} command - Código del comando.
   * @return {string} - Representación del comando en texto.
   */
  const convertCommandString = (command) => {
    command = parseInt(command);
    if (command === STANDBY) return "STANDBY";
    else if (command === SIT ) return "SIT";
    else if (command === WALK) return "WALK";
    else if (command === ROTATE ) return "ROTATE";
    else if (command === STANDUP) return "STANDUP";
    else return null;
  };

  /**
   * Convierte el código del usuario a su nombre correspondiente.
   * @param {number} user - Código del usuario.
   * @return {string} - Nombre del usuario.
   */
  const convertUserString = (user) => {
    user = parseInt(user);
    if (user === 0) return "Gerard";
    else if (user === 1) return "Albert";
    else if (user === 2) return "Adri";
    else if (user === 3) return "Raul";
    else return null;
  };

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
    console.log("submit token ", token);
  }

  /**
   * Maneja los datos de audio disponibles.
   * @param {Event} event - Evento que contiene los datos de audio.
   */
  const handleDataAvailable = (event) => {
    audioChunks.push(event.data);
  };

  /**
   * Maneja la detención de la grabación y sube el archivo al servidor.
   */
  const handleStop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    audioChunks = [];

    const fileName = `${Date.now()}_${token}.wav`;
    const formData = new FormData();
    formData.append("audio", audioBlob, fileName);
    formData.append("token", token);

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("Audio uploaded successfully!");
      } else {
        alert("Failed to upload audio");
      }
    } catch (error) {
      console.error("Error uploading audio:", error);
      alert("Error uploading audio");
    }
  };

  /**
   * Inicia la grabación de audio.
   */
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

  /**
   * Detiene la grabación de audio.
   */
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

  /**
   * Maneja los comandos aceptados.
   */
  socket.on("command-accepted", ({ userToken, person, text, command }) => {
    //se setea la variable commandToken con el token del usuario que esta utilizando el robot
    commandToken = userToken;

    textSection.textContent = text;
    commandSection.textContent = convertCommandString(command);

    //si el comando es mio
    if (token === userToken) {
      //si el comando es WALK
      if (parseInt(command) !== 5) recordButton.disabled = true;
      alert("Robot is now being used by " + convertUserString(person));
      textSection.style.color = "green";
    } else {
      alert("Robot is being used by " + convertUserString(person));
      textSection.style.color = "red";
      recordButton.disabled = true;
    }
  });

  /**
   * Indica que vuelve a estado Standby por lo tanto nadie está utilizando robot
   */
  socket.on("go-standby", () => {
    commandToken = null;
    alert("Robot is now available");
    recordButton.disabled = false;
    textSection.textContent = "";
    commandSection.textContent = "";
  });

  /**
   * Habilita el botón de grabación si el token es aceptado.
   */
  socket.on("token-accepted", ({userToken, person, text, command}) => {
    console.log("token accepted")
    console.log(userToken, person, text, command);
    commandToken = userToken;    
    if (commandToken){
      alert("Robot is being used by " + convertUserString(person));
      textSection.textContent = text;
      textSection.style.color = "red";
      commandSection.textContent = convertCommandString(command);
      recordButton.disabled = true;
    }
    else {
      recordButton.disabled = false;
    }
  });

  /**
   * Finaliza el comando actual
   */
  socket.on("finish-command", ({userToken}) => {

    //si el comando es mio
    if (token === userToken) {
      recordButton.disabled = false;
    }
  })
  /**
   * Cada vez que se recarga la pagina, y se ha verificado el token
   */
  socket.on("is-command", ({ userToken, person, text, command, finished }) => {
    commandSection.textContent = convertCommandString(command);
    textSection.textContent = text;

    //si hay un comando en curso
    if (userToken){
      //si el comando eso mio
      if (token === userToken) {
        //si el usuario utilizando el robot es diferentes al que habia 
        if(commandToken !== userToken){
          alert("Robot is being used by you, " + convertUserString(person));
        }
        textSection.style.color = "green";

        //si esta finalizado
        console.log(finished)
        if (finished) recordButton.disabled = false;
        //si no esta finalizado
        else recordButton.disabled = true;

      } else {
        //si el comando no es mio
        alert("Robot is being used by " + convertUserString(person));
        textSection.style.color = "red";
        recordButton.disabled = true;
      }
    }
    else{
      //si no hay comando
      recordButton.disabled = false;
    }
  });
  /**
   * Gestiona la existencia del token.
   */
  socket.on("token-exists", (exists) => {
    if (exists){
      socket.emit('check-command');  
    }
    if (!exists){
      token = uuid.v4(); // Genera un nuevo token si el existente no es válido
      localStorage.setItem('token', token); // Guarda el nuevo token en localStorage
      socket.emit('submit-token', token); // Envía el nuevo token al servidor
    }
  });
});
