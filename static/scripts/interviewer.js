document.addEventListener("DOMContentLoaded", () => {
  const rubricInput = document.getElementById("rubricInput");
  const rubricPreview = document.getElementById("rubricPreview");
  const transcriptList = document.getElementById("transcriptList");
  const submitEvalButton = document.getElementById("submitEvalButton");
  const evaluationSummary = document.getElementById("evaluationSummary");

  let selectedTranscript = null;
  let parsedRubric = [];

  function parseRubric(csvText) {
    rubricPreview.textContent = csvText;
    parsedRubric = csvText.trim().split("\n").slice(1).map(line => {
      const [skill, level, score, description] = line.split(",");
      return { skill, level, score: Number(score), description };
    });
  }

  rubricInput.addEventListener("change", () => {
    const file = rubricInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => parseRubric(e.target.result);
      reader.readAsText(file);
    }
  });

  function fetchTranscripts() {
  fetch("/transcripts")
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch transcripts.");
      return response.json();
    })
    .then(data => {
      console.log("[DEBUG] Raw transcript data received:", data);

      const transcriptList = document.getElementById("transcriptList");
      transcriptList.innerHTML = "";

      if (!Array.isArray(data) || data.length === 0) {
        console.warn("[DEBUG] No valid transcripts found.");
        transcriptList.innerHTML = "<li>No transcripts available.</li>";
        return;
      }

      data.forEach((item, index) => {
        const name = item.name || "Unknown";
        const submittedAt = item.submitted_at ? new Date(item.submitted_at) : null;
        const formattedTime = submittedAt ? submittedAt.toLocaleString("en-US", {
          month: "short", day: "numeric", year: "numeric",
          hour: "2-digit", minute: "2-digit", hour12: true
        }) : "[no time]";

        console.log(`[DEBUG] Processing transcript ${index + 1}:`, name, formattedTime);

        const li = document.createElement("li");
        const button = document.createElement("button");
        button.textContent = `${name} – ${formattedTime}`;
        button.className = "transcript-button";
        button.addEventListener("click", () => {
          console.log("[DEBUG] Transcript selected:", item);
          displayTranscript(item);
        });

        li.appendChild(button);
        transcriptList.appendChild(li);
      });
    })
    .catch(error => {
      console.error("[ERROR] Failed to load transcripts:", error);
    });
}

  submitEvalButton.addEventListener("click", () => {
    if (!selectedTranscript || !parsedRubric.length) {
      alert("Select a transcript and load a rubric before submitting.");
      return;
    }

    fetch("/evaluate-transcript", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        rubric: parsedRubric,
        transcript: selectedTranscript.transcript,
        name: selectedTranscript.name || "Unknown",
        email: selectedTranscript.email || "Unknown"
      })
    })
      .then(res => res.json())
      .then(data => {
        evaluationSummary.textContent = data.result || "Evaluation complete, but no result returned.";
      })
      .catch(err => {
        console.error("Evaluation submission failed:", err);
        evaluationSummary.textContent = "Failed to submit for evaluation.";
      });
  });

  fetchTranscripts();
});
