document.addEventListener("DOMContentLoaded", () => {
  const promptEl = document.getElementById("questionPrompt");
  if (promptEl) {
    promptEl.innerHTML = "Please describe a project you've worked on and explain your process.";
  }

  const recordButton = document.getElementById("recordButton");
  const stopButton = document.getElementById("stopButton");
  const transcriptSection = document.getElementById("transcriptSection");
  const transcriptPreview = document.getElementById("transcriptPreview");
  const submitBtn = document.getElementById("submitTranscriptBtn");
  const timerDisplay = document.getElementById("timerDisplay");

  let mediaRecorder;
  let audioChunks = [];
  let timer;
  let timeLeft = 3600; // 60 minutes

  function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
    document.title = `⏱ ${minutes}:${seconds.toString().padStart(2, "0")} – SkillScope`;
    if (timeLeft > 0) {
      timeLeft--;
    } else {
      clearInterval(timer);
      stopRecording();
    }
  }

  function startTimer() {
    timer = setInterval(updateTimer, 1000);
    updateTimer();
  }

  function stopRecording() {
    mediaRecorder.stop();
    recordButton.classList.remove("hidden");
    stopButton.classList.add("hidden");
  }

  recordButton.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const reader = new FileReader();
      reader.onload = () => {
        // simulate a transcript preview
        transcriptPreview.textContent = "[00:00 → 00:05] This is a sample transcript.";
        transcriptSection.classList.remove("hidden");
        submitBtn.classList.remove("hidden");
      };
      reader.readAsDataURL(audioBlob);
    });

    recordButton.classList.add("hidden");
    stopButton.classList.remove("hidden");
    startTimer();
  });

  stopButton.addEventListener("click", () => {
    stopRecording();
  });

  submitBtn.addEventListener("click", () => {
    alert("Transcript submitted!");
  });
});
