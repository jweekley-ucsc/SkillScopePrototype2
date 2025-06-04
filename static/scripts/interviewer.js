document.addEventListener("DOMContentLoaded", () => {
  const rubricInput = document.getElementById("rubricInput");
  const rubricPreview = document.getElementById("rubricPreview");
  const transcriptList = document.getElementById("transcriptList");
  const submitEvalButton = document.getElementById("submitEvalButton");
  const evaluationSummary = document.getElementById("evaluationSummary");

  let rubricCSV = "";

  function fetchTranscripts() {
    fetch("/list-transcripts")
      .then(res => res.json())
      .then(files => {
        transcriptList.innerHTML = "";
        files.forEach(name => {
          const li = document.createElement("li");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.value = name;
          li.appendChild(checkbox);
          li.appendChild(document.createTextNode(" " + name));
          transcriptList.appendChild(li);
        });
      });
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
    const selected = Array.from(transcriptList.querySelectorAll("input[type='checkbox']:checked"))
      .map(cb => cb.value);
    if (!rubricCSV || selected.length === 0) {
      alert("Please upload a rubric and select at least one transcript.");
      return;
    }

    fetch("/evaluate-transcripts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rubric: rubricCSV, transcripts: selected })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        evaluationSummary.textContent = "Evaluation submitted successfully.";
      } else {
        evaluationSummary.textContent = "Evaluation failed.";
      }
    });
  });

  fetchTranscripts();
});
