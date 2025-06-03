document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const errorMessage = document.getElementById("errorMessage");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = form.name.value.trim();
    const email = form.email.value.trim().toLowerCase();

    if (!name || !email) {
      errorMessage.textContent = "Please enter both name and email.";
      errorMessage.classList.remove("hidden");
      return;
    }

    const submittedEmails = JSON.parse(localStorage.getItem("submittedEmails") || "[]");
    if (submittedEmails.includes(email)) {
      errorMessage.textContent = "You have already completed this assessment.";
      errorMessage.classList.remove("hidden");
      return;
    }

    try {
      const res = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data?.error || "Registration failed.");
      }

      submittedEmails.push(email);
      localStorage.setItem("submittedEmails", JSON.stringify(submittedEmails));
      window.location.href = `/interview?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`;

    } catch (err) {
      errorMessage.textContent = err.message;
      errorMessage.classList.remove("hidden");
    }
  });
});
