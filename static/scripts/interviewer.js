document.addEventListener("DOMContentLoaded", () => {
  const rubricInput = document.getElementById("rubricInput");
  const rubricPreview = document.getElementById("rubricPreview");
  const transcriptList = document.getElementById("transcriptList");
  const submitEvalButton = document.getElementById("submitEvalButton");
  const evaluationSummary = document.getElementById("evaluationSummary");
  const transcriptPreview = document.getElementById("transcriptPreview");
  const selectAllBtn = document.getElementById("selectAllBtn");

  let rubricCSV = "";
  const selectedTranscripts = new Set();
  let allTranscripts = [];

  function fetchTranscripts() {
    fetch("/transcripts")
      .then(res => res.json())
      .then(data => {
        allTranscripts = data;
        transcriptList.innerHTML = "";

        data.forEach((entry, index) => {
          const name = entry.name || "Unknown";
          const time = entry.submitted_at || entry.timestamp || "no time";
          const label = `${name} – ${new Date(time).toLocaleString()}`;

          const btn = document.createElement("button");
          btn.className = "transcript-button";
          btn.textContent = label;
          btn.dataset.index = index;

          btn.addEventListener("click", () => {
            const key = JSON.stringify(entry);
            const isSelected = selectedTranscripts.has(key);

            if (isSelected) {
              selectedTranscripts.delete(key);
              btn.classList.remove("selected");
              btn.style.backgroundColor = "";
            } else {
              selectedTranscripts.add(key);
              btn.classList.add("selected");
              btn.style.backgroundColor = "#1e7f3c"; // dark green
              btn.style.color = "#fff";
            }

            updateTranscriptPreview();
          });

          transcriptList.appendChild(btn);
        });
      })
      .catch(err => {
        transcriptList.innerHTML = "Failed to load transcripts.";
        console.error("Transcript load error:", err);
      });
  }

  function updateTranscriptPreview() {
    const selectedArray = Array.from(selectedTranscripts).map(x => JSON.parse(x));

    if (selectedArray.length === 1) {
      const t = selectedArray[0];
      transcriptPreview.textContent = `[${t.name} – ${t.submitted_at}]\n\n${t.transcript}`;
    } else if (selectedArray.length > 1) {
      transcriptPreview.textContent = selectedArray.map(t => `${t.name} – ${t.submitted_at}`).join("\n");
    } else {
      transcriptPreview.textContent = "No transcript selected.";
    }
  }

  function parseRubric(input) {
    rubricCSV = input.trim();
    rubricPreview.textContent = rubricCSV || "No rubric provided.";
  }

  rubricInput.addEventListener("change", () => {
    const file = rubricInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => parseRubric(e.target.result);
      reader.readAsText(file);
    }
  });

  submitEvalButton.addEventListener("click", () => {
  if (!rubricCSV || selectedTranscripts.size === 0) {
    alert("Please upload a rubric and select at least one transcript.");
    return;
  }

  const payload = Array.from(selectedTranscripts).map(x => JSON.parse(x)).map(entry => ({
    name: entry.name || "Unknown",
    email: entry.email || "unknown@none.edu",
    transcript: entry.transcript,
    submitted_at: entry.submitted_at || entry.timestamp || "unknown"
  }));

  fetch("/evaluate-transcripts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rubric_csv: rubricCSV, transcripts: payload })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
  let summaryText = `${data.result || "Evaluated"}\n\n`;

  if (data.evaluations && Array.isArray(data.evaluations)) {
    data.evaluations.forEach(entry => {
      summaryText += `🔹 ${entry.name} (${entry.email})\n`;
      if (entry.error) {
        summaryText += `  ❌ Error: ${entry.error}\n\n`;
      } else {
        Object.entries(entry.score).forEach(([skill, result]) => {
          summaryText += `  • ${skill}: ${result.level} (${result.score}) – ${result.description}\n`;
        });
        summaryText += `\n`;
      }
    });
  }

  evaluationSummary.textContent = summaryText.trim();


if (data.evaluations && Array.isArray(data.evaluations)) {
  data.evaluations.forEach(entry => {
    summaryText += `🔹 ${entry.name} (${entry.email})\n`;

    if (entry.error) {
      summaryText += `  ❌ Error: ${entry.error}\n\n`;
    } else {
      Object.entries(entry.score).forEach(([skill, result]) => {
        summaryText += `  • ${skill}: ${result.level} (${result.score}) – ${result.description}\n`;
      });
      summaryText += `\n`;
    }
  });
}

evaluationSummary.textContent = summaryText.trim();

      selectedTranscripts.clear();
      fetchTranscripts();
      updateTranscriptPreview();

      // Trigger LLM eval request generation
      fetch("/generate-eval-request", { method: "POST" })
        .then(evalRes => evalRes.json())
        .then(evalData => {
          console.log(`✅ Eval request generated: ${evalData.appended || 0} transcripts`);
        })
        .catch(err => {
          console.error("❌ Failed to generate eval request:", err);
        });

    } else {
      evaluationSummary.textContent = "Evaluation failed: " + (data.error || "Unknown error");
    }
  })
  .catch(err => {
    evaluationSummary.textContent = "Evaluation request failed.";
    console.error("Evaluation submission error:", err);
  });
});


  selectAllBtn.addEventListener("click", () => {
    selectedTranscripts.clear();
    const buttons = document.querySelectorAll(".transcript-button");
    buttons.forEach((btn, index) => {
      const entry = allTranscripts[index];
      const key = JSON.stringify(entry);
      selectedTranscripts.add(key);
      btn.classList.add("selected");
      btn.style.backgroundColor = "#1e7f3c";
      btn.style.color = "#fff";
    });
    updateTranscriptPreview();
  });

  fetchTranscripts();
});
