// static/scripts/evaluate.js

document.addEventListener("DOMContentLoaded", () => {
  const fileSelect = document.getElementById("evalFileSelect");
  const usedFilesBox = document.getElementById("usedFiles");
  const resultsBox = document.getElementById("results");
  const errorsBox = document.getElementById("errorMessages");

  async function loadEvaluationFiles() {
    try {
      const res = await fetch("/list-evaluation-files");
      const filenames = await res.json();
      fileSelect.innerHTML = filenames.map(
        (f) => `<option value="${f}">${f}</option>`
      ).join("");
      if (filenames.length > 0) {
        loadEvaluation(filenames[0]);
      }
    } catch (err) {
      console.error("Failed to load evaluation list:", err);
      errorsBox.textContent = "Could not load evaluation files.";
    }
  }

  async function loadEvaluation(filename) {
    try {
      const res = await fetch(`/get-evaluation-file?filename=${encodeURIComponent(filename)}`);
      const lines = await res.text();
      const records = lines
        .split("\n")
        .filter(Boolean)
        .map((line) => JSON.parse(line));

      const displayParts = [];
      const fileInfoParts = [];
      const errorParts = [];

      records.forEach((record) => {
        if (record.error) {
          errorParts.push(`🔴 ${record.email}: ${record.error}`);
        } else if (record.feedback) {
          displayParts.push(`📝 ${record.email}:\n${record.feedback}`);
        }

        // Metadata to show rubric/prompt if available
        if (record.prompt_path || record.rubric_path) {
          fileInfoParts.push(`📄 Prompt: ${record.prompt_path || "unknown"}\n📊 Rubric: ${record.rubric_path || "unknown"}`);
        }
      });

      resultsBox.textContent = displayParts.join("\n\n");
      usedFilesBox.textContent = fileInfoParts.join("\n\n") || "Prompt and rubric not recorded.";
      errorsBox.textContent = errorParts.join("\n") || "No errors reported.";
    } catch (err) {
      console.error("Failed to load selected evaluation file:", err);
      errorsBox.textContent = "Failed to parse evaluation file.";
    }
  }

  fileSelect.addEventListener("change", (e) => {
    const filename = e.target.value;
    if (filename) {
      loadEvaluation(filename);
    }
  });

  loadEvaluationFiles();
});
