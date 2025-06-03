async function fetchInterviewSets() {
  try {
    const response = await fetch("http://127.0.0.1:5050/interview-sets");
    const sets = await response.json();

    const container = document.getElementById("setsContainer");
    container.innerHTML = "";

    if (sets.length === 0) {
      container.innerHTML = "<p class='text-center text-gray-600'>No interview sets submitted yet.</p>";
      return;
    }

    sets.forEach((set, index) => {
      const block = document.createElement("div");
      block.className = "bg-white p-6 rounded shadow";

      block.innerHTML = `
        <h2 class="text-xl font-semibold mb-2">Set ${index + 1}: ${set.name}</h2>
        <div class="mb-4">
          <h3 class="font-medium text-gray-700">Interview Questions:</h3>
          <pre class="bg-gray-50 p-3 rounded whitespace-pre-wrap text-sm">${set.questions}</pre>
        </div>
        <div>
          <h3 class="font-medium text-gray-700">Rubric Preview:</h3>
          <pre class="bg-gray-50 p-3 rounded whitespace-pre-wrap text-sm overflow-x-auto">${set.rubric_csv}</pre>
        </div>
      `;
      container.appendChild(block);
    });
  } catch (err) {
    console.error("Failed to load interview sets:", err);
    document.getElementById("setsContainer").innerHTML =
      "<p class='text-center text-red-600'>Failed to load interview sets. See console for details.</p>";
  }
}

// Call on page load
fetchInterviewSets();
