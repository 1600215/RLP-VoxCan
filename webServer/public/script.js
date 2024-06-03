document.addEventListener("DOMContentLoaded", () => {
  let mediaRecorder;
  let audioChunks = [];
  const recordButton = document.getElementById("recordButton");
  const submitNameButton = document.getElementById("submitNameButton");
  const nameInput = document.getElementById("nameInput");
  const nameSection = document.getElementById("nameSection");
  const recordSection = document.getElementById("recordSection");
  const title = document.getElementById("title");
  let recording = false;
  let name;
  const socket = io();

  // Retrieve name from localStorage
  const savedName = localStorage.getItem('name');

  if (savedName) {
      name = savedName;
      socket.emit('check-name', name);
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

  submitNameButton.addEventListener("click", () => {
      const nameValue = nameInput.value.trim();
      if (nameValue) {
          name = nameValue;
          localStorage.setItem('name', name); // Save name in localStorage
          socket.emit('submit-name', name);
      } else {
          alert("Please enter a name.");
      }
  });

  socket.on("name-accepted", (accepted) => {
      if (accepted) {
          alert(`Name accepted: ${name}. You can start recording.`);
          nameSection.style.display = "none";
          recordSection.style.display = "block";
          recordButton.disabled = false;
          title.textContent = `Fogueado - ${name}`; // Update title with name
      } else {
          alert("Invalid name. You cannot record.");
          recordButton.disabled = true;
      }
  });

  socket.on("name-exists", (exists) => {
      if (exists) {
          alert(`Welcome back, ${name}. You can start recording.`);
          nameSection.style.display = "none";
          recordSection.style.display = "block";
          recordButton.disabled = false;
          title.textContent = `Fogueado - ${name}`; // Update title with name
      } else {
          alert("Your name is not recognized. Please enter your name again.");
          localStorage.removeItem('name');
          nameSection.style.display = "block";
          recordSection.style.display = "none";
          recordButton.disabled = true;
      }
  });
});
