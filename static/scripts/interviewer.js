document.addEventListener("DOMContentLoaded", () => {
  const rubricInput = document.getElementById("rubricInput");
  const rubricPreview = document.getElementById("rubricPreview");
  const transcriptList = document.getElementById("transcriptList");
  const submitEvalButton = document.getElementById("submitEvalButton");
  const evaluationSummary = document.getElementById("evaluationSummary");

  let selectedTranscript = null;
  let parsedRubric = [];

  // Renders the rubric to the preview window
  function parseRubric(csvText) {
    rubricPreview.textContent = csvText;
    parsedRubric = csvText.trim().split("\n").slice(1).map(line => {
      const [skill, level, score, description] = line.split(",");
      return { skill, level, score: Number(score), description };
    });
  }

  // Upload handler for rubric
  rubricInput.addEventListener("change", () => {
    const file = rubricInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => parseRubric(e.target.result);
      reader.readAsText(file);
    }
  });

  // Fetch and display list of transcripts
  function fetchTranscripts() {
    fetch("/transcripts")
      .then(res => res.json())
      .then(data => {
        transcriptList.innerHTML = "";
        if (!data.length) {
          transcriptList.innerHTML = "<li>No transcripts available.</li>";
          return;
        }

        data.forEach((entry, index) => {
          const li = document.createElement("li");
          li.className = "transcript-item";

          const name = entry.name || "Unknown";
          const ts = new Date(entry.submitted_at || entry.timestamp || Date.now());
          const readableDate = ts.toLocaleString();

          li.innerHTML = `<button class="transcript-btn" data-index="${index}">${name} – ${readableDate}</button>`;
          li.querySelector("button").addEventListener("click", () => {
            selectedTranscript = entry;
            evaluationSummary.textContent = entry.transcript || "[No content]";
          });

          transcriptList.appendChild(li);
        });
      })
      .catch(err => {
        console.error("Transcript load error:", err);
        transcriptList.innerHTML = "<li>Failed to load transcripts.</li>";
      });
  }

  // Submission handler for evaluation
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
        email: selectedTranscript.email || "unknown",
        name: selectedTranscript.name || "unknown"
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

  // Trigger initial fetch
  fetchTranscripts();
});
