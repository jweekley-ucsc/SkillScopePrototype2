
document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startButton");
    const stopBtn = document.getElementById("stopButton");
    const transcribeBtn = document.getElementById("transcribeButton");
    const submitBtn = document.getElementById("submitTranscriptButton");
    const reflectionInput = document.getElementById("reflectionInput");
    const transcriptPreview = document.getElementById("transcriptPreview");
    const timerDisplay = document.getElementById("timerDisplay");

    let mediaRecorder;
    let recordedChunks = [];
    let sessionId = Date.now() + '-' + Math.random().toString(36).substring(2, 10);
    let timer;
    let timeLeft = 60 * 60;

    function startTimer() {
        if (!timerDisplay) return;

        function updateTimer() {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
            document.title = `Time Left: ${minutes}:${seconds.toString().padStart(2, "0")}`;

            if (timeLeft > 0) {
                timeLeft--;
            } else {
                clearInterval(timer);
            }
        }

        updateTimer();
        timer = setInterval(updateTimer, 1000);
    }

    function stopTimer() {
        clearInterval(timer);
    }

    function uploadRecording(blob) {
        const formData = new FormData();
        const filename = `${sessionId}.webm`;
        formData.append("audio", blob, filename);
        formData.append("filename", filename);

        fetch("/upload-audio", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("Upload successful.");
                if (transcribeBtn) transcribeBtn.style.display = "block";
            } else {
                console.error("Upload failed:", data.error);
            }
        })
        .catch(err => console.error("Upload error:", err));
    }

    function fetchTranscript() {
        fetch(`/transcribe?session_id=${sessionId}`)
            .then(res => res.json())
            .then(data => {
                if (data && data.text && transcriptPreview) {
                    transcriptPreview.textContent = data.text;
                    if (submitBtn) submitBtn.style.display = "block";
                } else {
                    transcriptPreview.textContent = "No transcript available.";
                }
            })
            .catch(err => {
                if (transcriptPreview) transcriptPreview.textContent = "Transcription failed.";
                console.error("Transcription error:", err);
            });
    }

    if (startBtn) {
        startBtn.addEventListener("click", () => {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];

                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) recordedChunks.push(e.data);
                };

                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: "audio/webm" });
                    uploadRecording(blob);
                    stopTimer();
                };

                mediaRecorder.start();
                startBtn.disabled = true;
                if (stopBtn) stopBtn.disabled = false;
                startTimer();
            });
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener("click", () => {
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
                stopBtn.disabled = true;
            }
        });
    }

    if (transcribeBtn) {
        transcribeBtn.addEventListener("click", () => {
            fetchTranscript();
            transcribeBtn.disabled = true;
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener("click", () => {
            const email = localStorage.getItem("email");
            const transcript = transcriptPreview ? transcriptPreview.textContent : "";
            const reflection = reflectionInput ? reflectionInput.value : "";

            fetch("/submit-transcript", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, transcript, reflection })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("Package submitted successfully.");
                } else {
                    alert("Submission failed.");
                }
            });
        });
    }
});
