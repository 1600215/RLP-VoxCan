let mediaRecorder;
let audioChunks = [];
const recordButton = document.getElementById("recordButton");
let recording = false;

recordButton.addEventListener("click", async () => {
  if (!recording) {
    // Start recording
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.wav");

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
    mediaRecorder.start();
    recordButton.textContent = "Stop Recording";
  } else {
    // Stop recording
    mediaRecorder.stop();
    recordButton.textContent = "Start Recording";
  }
  recording = !recording;
});
