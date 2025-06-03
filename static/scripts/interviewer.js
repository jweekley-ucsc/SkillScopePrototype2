
document.addEventListener("DOMContentLoaded", () => {
  const rubricUpload = document.getElementById("rubricUpload");
  const promptUpload = document.getElementById("promptUpload");
  const submitSelectedBtn = document.getElementById("submitSelected");
  const submitAllBtn = document.getElementById("submitAll");
  const rubricPreview = document.getElementById("rubricPreview");
  const promptPreview = document.getElementById("promptPreview");
  const transcriptList = document.getElementById("submissionList");
  const transcriptBox = document.getElementById("transcriptBox");

  let rubricPath = "";
  let promptPath = "";
  let submissions = [];

  async function loadSubmissions() {
    try {
      const res = await fetch("/submissions");
      const data = await res.json();
      submissions = data.filter((d) => d.transcript);
      transcriptList.innerHTML = "";
      submissions.forEach((entry, index) => {
        const li = document.createElement("li");
        li.className = "cursor-pointer p-2 border-b hover:bg-gray-50";
        li.textContent = `${entry.name || "No Name"} <${entry.email}>`;
        li.addEventListener("click", () => {
          transcriptBox.textContent = entry.transcript;
          document.getElementById("transcriptPanel").classList.remove("hidden");
          transcriptBox.scrollIntoView({ behavior: "smooth" });
          transcriptBox.dataset.selectedIndex = index;
        });
        transcriptList.appendChild(li);
      });
    } catch (err) {
      console.error("Failed to load submissions:", err);
    }
  }

  rubricUpload.addEventListener("change", () => {
    const file = rubricUpload.files[0];
    if (!file) return;
    rubricPath = `instance/rubrics/${file.name}`;
    rubricPreview.textContent = file.name;
  });

  promptUpload.addEventListener("change", () => {
    const file = promptUpload.files[0];
    if (!file) return;
    promptPath = `instance/prompts/${file.name}`;
    promptPreview.textContent = file.name;
  });

  async function submitToLLM(selectedOnly = false) {
    const selectedIndex = parseInt(transcriptBox.dataset.selectedIndex);
    const targets = selectedOnly
      ? [submissions[selectedIndex]]
      : submissions;

    if (!rubricPath || !promptPath || targets.length === 0) {
      alert("Missing rubric, prompt, or submissions");
      return;
    }

    const payload = targets.map((entry) => ({
      email: entry.email,
      transcript: entry.transcript,
      rubric_path: rubricPath,
      prompt_path: promptPath,
    }));

    try {
      const res = await fetch("/submit-evaluation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (result.status === "ok") {
        window.open("/evaluate", "_blank");
      } else {
        throw new Error(result.message || "Unknown error");
      }
    } catch (err) {
      console.error("Submission error:", err);
      alert("LLM evaluation failed: " + err.message);
    }
  }

  submitSelectedBtn.addEventListener("click", () => submitToLLM(true));
  submitAllBtn.addEventListener("click", () => submitToLLM(false));

  loadSubmissions();
});