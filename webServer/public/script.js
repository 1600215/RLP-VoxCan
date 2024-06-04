function generateToken() {
  const token = uuidv4();
  return token;
}

document.addEventListener("DOMContentLoaded", () => {
  let mediaRecorder;
  let audioChunks = [];
  const recordButton = document.getElementById("recordButton");
  const title = document.getElementById("title");


  let recording = false;
  let token;
  let command = null;

  const socket = io();

  // Retrieve name from localStorage
  const savedToken = localStorage.getItem('token');
  if (savedToken) {
      token = savedToken;
      socket.emit('check-token', token);
  }else{
        token = generateToken();
        console.log(token);
  }

  const handleDataAvailable = (event) => {
      audioChunks.push(event.data);
  };

  const handleStop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      audioChunks = [];
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("name", name);

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

  const startRecording = async () => {
      try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = handleDataAvailable;
          mediaRecorder.onstop = handleStop;
          mediaRecorder.start();
          recordButton.textContent = "Stop Recording";
          recording = true;
      } catch (error) {
          console.error("Error accessing media devices:", error);
          alert("Error accessing media devices");
      }
  };

  const stopRecording = () => {
      mediaRecorder.stop();
      recordButton.textContent = "Start Recording";
      recording = false;
  };

  recordButton.addEventListener("click", () => {
      if (!recording) {
          startRecording();
      } else {
          stopRecording();
      }
  });


  socket.on("CommandAccepted", (userToken) => {
    command = userToken;
    if(token === userToken){
        alert("Robot is now being used by you");
        recordButton.disabled = true;
    }
    else{
        alert("Robot is being used by another user");
        recordButton.disabled = true; 
    }
  });

  socket.on("OnCommand", (userToken) => {
    command = userToken;
    if(token === userToken){
        alert("Robot is now being used by you");
    }
    else{
        alert("Robot is being used by another user");
    }
    recordButton.disabled = true; 
  });

  socket.on("commandFinished", () => {
    command = null;
    alert("Robot is now available");
    recordButton.disabled = false;
  });

  socket.on("token-exists", (exists) => {
      if (exists) {
          alert(`Welcome back, ${token}`);
          if (command) {
              recordButton.disabled = true;
          } else {
              recordButton.disabled = false;
          }
          title.textContent = `LOGUEADO - ${name}`; // Update title with name
      } else {
          alert("Your name is not recognized. Please enter your name again.");
          localStorage.removeItem('token');
          token = generateToken();
          recordButton.disabled = true;
      }
  });
});
