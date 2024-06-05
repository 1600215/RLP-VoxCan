document.addEventListener("DOMContentLoaded", () => {
  let mediaRecorder;
  let audioChunks = [];
  const recordButton = document.getElementById("recordButton");


  let recording = false;
  let token;
  let command = null;

  const socket = io();

  // Retrieve name from localStorage
  const savedToken = localStorage.getItem('token');
  if (savedToken) {
      token = savedToken;
      recordButton.disabled = true;
      socket.emit('check-token', token);
      console.log("check-token", token);

  }else{
        token = uuid.v4();
        localStorage.setItem('token', token);
        socket.emit('submit-token', token);
        console.log("submit token ",token);
  }
 
  const handleDataAvailable = (event) => {
      audioChunks.push(event.data);
  };

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

  socket.on("token-accepted", () => {
      recordButton.disabled = false;
  });

  socket.on("token-exists", (exists) => {
      if (exists) {
          if (command) {
              recordButton.disabled = true;
          } else {
              recordButton.disabled = false;
          }
      } else {
          token = uuid.v4();
          localStorage.setItem('token', token);
          socket.emit('submit-token', token);
          recordButton.disabled = true;

      }
  });
});
