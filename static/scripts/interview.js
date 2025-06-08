document.addEventListener("DOMContentLoaded", () => {
    const startButton = document.getElementById("startButton");
    const stopButton = document.getElementById("stopButton");
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

    async function uploadRecording(blob, sessionId) {
    const formData = new FormData();
    const filename = `${sessionId}.webm`;
    formData.append("audio", blob, filename);
    formData.append("filename", filename);

    try {
        const res = await fetch("/upload-audio", {
            method: "POST",
            body: formData
        });

        const contentType = res.headers.get("Content-Type");
        if (!res.ok) {
            const errorText = await res.text();
            console.error("❌ Server returned error page:", errorText);
            throw new Error(`Upload failed with status ${res.status}`);
        }

        if (!contentType || !contentType.includes("application/json")) {
            const text = await res.text();
            console.error("❌ Response not JSON:", text);
            throw new Error("Expected JSON but received something else.");
        }

        const data = await res.json();
        if (data.success || data.status === "success") {
            console.log("✅ Upload successful:", data);
            const transcriptBox = document.getElementById("transcriptPreview");
            if (transcriptBox) {
                transcriptBox.textContent = "Transcribing... please wait.";
            }

            await fetchTranscript(filename);  // Automatically begin transcription

            const stopButton = document.getElementById("stopButton");
            if (stopButton) stopButton.disabled = true;
        } else {
            throw new Error("Upload failed: " + (data.error || "Unknown error"));
        }
    } catch (err) {
        console.error("❌ Upload error:", err);
        alert("Upload failed. See console for details.");
    }
}


    async function fetchTranscript(filename) {
        try {
            const response = await fetch("/transcribe", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename })
            });

            const result = await response.json();

            if (result.success && result.transcript) {
                transcriptPreview.textContent = result.transcript;
                submitButton.style.display = "block";
            } else {
                console.error("❌ Transcription failed:", result.error);
                transcriptPreview.textContent = "Transcription failed.";
            }
        } catch (err) {
            console.error("Transcript fetch failed:", err);
            transcriptPreview.textContent = "Error fetching transcript.";
        }
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
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
            stopButton.disabled = true;
        }
    });

    submitButton.addEventListener("click", () => {
        const email = localStorage.getItem("skillScopeUserEmail");
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
                localStorage.removeItem("sessionId");
            } else {
                alert("Submission failed.");
            }
        });
    });

    // ⏱️ Automatically start timer on page load
    startTimer();
});
