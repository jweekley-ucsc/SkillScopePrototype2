document.addEventListener("DOMContentLoaded", () => {
    const startButton = document.getElementById("startButton");
    const stopButton = document.getElementById("stopButton");
    const transcribeButton = document.getElementById("transcribeButton");
    const submitButton = document.getElementById("submitTranscriptButton");
    const reflectionInput = document.getElementById("reflectionInput");
    const transcriptPreview = document.getElementById("transcriptPreview");

    let mediaRecorder;
    let recordedChunks = [];
    let sessionId = localStorage.getItem("sessionId") || (Date.now() + '-' + Math.random().toString(36).substring(2, 10));
    localStorage.setItem("sessionId", sessionId);
    let timer;
    let timeLeft = 60 * 60;

    function startTimer() {
        const timerDisplay = document.getElementById("timerDisplay");
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

    function uploadRecording(blob, sessionId) {
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
                transcribeButton.style.display = "block";
                stopButton.disabled = true;
            } else {
                console.error("Upload failed:", data.error);
            }
        })
        .catch(err => {
            console.error("Upload error:", err);
        });
    }

    function fetchTranscript(sessionId) {
        fetch(`/transcribe?session_id=${sessionId}`)
            .then(res => res.json())
            .then(data => {
                if (data.text) {
                    transcriptPreview.textContent = data.text;
                    submitButton.style.display = "block";
                } else {
                    transcriptPreview.textContent = "No transcript available.";
                }
            })
            .catch(err => {
                console.error("Transcript fetch failed:", err);
                transcriptPreview.textContent = "Error fetching transcript.";
            });
    }

    startButton.addEventListener("click", () => {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            recordedChunks = [];

            mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0) recordedChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: "audio/webm" });
                uploadRecording(blob, sessionId);
                stopTimer();
            };

            mediaRecorder.start();
            startButton.disabled = true;
            stopButton.disabled = false;
        });
    });

    stopButton.addEventListener("click", () => {
        mediaRecorder.stop();
    });

    transcribeButton.addEventListener("click", () => {
        transcribeButton.disabled = true;
        fetchTranscript(sessionId);
    });

    submitButton.addEventListener("click", () => {
        const email = localStorage.getItem("email");
        const transcript = transcriptPreview.textContent;
        const reflection = reflectionInput.value;

        if (!email || !transcript) {
            alert("Missing email or transcript.");
            return;
        }

        fetch("/submit-transcript", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, transcript, reflection })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Transcript submitted successfully.");
                localStorage.removeItem("sessionId"); // Prevent resubmission
            } else {
                alert("Submission failed.");
            }
        });
    });

    // ⏱️ Automatically start timer on page load
    startTimer();
});
