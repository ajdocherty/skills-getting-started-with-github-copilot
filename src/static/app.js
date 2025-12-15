document.addEventListener("DOMContentLoaded", () => {
  const activitiesListEl = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const template = document.getElementById("activity-card-template");

  let activities = [];
  let participantsByActivity = {}; // { activityId: [email, ...] }

  // Function to fetch activities and signups from API
  async function fetchActivitiesAndSignups() {
    try {
      const [aRes, sRes] = await Promise.all([
        fetch("/api/activities"),
        fetch("/api/signups"),
      ]);
      activities = await aRes.json(); // expect [{ id, name, description }]
      const signups = await sRes.json(); // expect [{ activityId, email }]

      participantsByActivity = {};
      signups.forEach((s) => {
        const id = String(s.activityId);
        participantsByActivity[id] = participantsByActivity[id] || [];
        participantsByActivity[id].push(s.email);
      });

      renderActivityOptions();
      renderActivities();
    } catch (err) {
      activitiesListEl.innerHTML = '<p class="error">Unable to load activities.</p>';
      console.error(err);
    }
  }

  function renderActivityOptions() {
    // clear existing dynamic options
    Array.from(activitySelect.querySelectorAll("option.dynamic")).forEach((o) => o.remove());
    activities.forEach((act) => {
      const opt = document.createElement("option");
      opt.value = act.id;
      opt.textContent = act.name;
      opt.classList.add("dynamic");
      activitySelect.appendChild(opt);
    });
  }

  function renderActivities() {
    activitiesListEl.innerHTML = "";
    activities.forEach((act) => {
      const id = String(act.id);
      const clone = template.content.cloneNode(true);
      const card = clone.querySelector(".activity-card");
      card.dataset.activityId = id;
      card.querySelector(".activity-title").textContent = act.name;
      card.querySelector(".activity-desc").textContent = act.description || "";

      const listEl = card.querySelector(".participants-list");
      const participants = participantsByActivity[id] || [];
      listEl.innerHTML = "";
      if (participants.length === 0) {
        const li = document.createElement("li");
        li.className = "empty";
        li.textContent = "No participants yet";
        listEl.appendChild(li);
      } else {
        participants.forEach((email) => {
          const li = document.createElement("li");
          li.textContent = email;
          listEl.appendChild(li);
        });
      }

      // join button fills email into form (small convenience)
      const joinBtn = card.querySelector(".join-btn");
      joinBtn.addEventListener("click", () => {
        activitySelect.value = id;
        document.getElementById("email").focus();
      });

      activitiesListEl.appendChild(clone);
    });
  }

  async function handleSignup(event) {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const activityId = document.getElementById("activity").value;
    if (!email || !activityId) return;

    try {
      const res = await fetch("/api/signups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, activityId }),
      });
      if (!res.ok) throw new Error("Signup failed");

      // optimistic UI update
      participantsByActivity[activityId] = participantsByActivity[activityId] || [];
      if (!participantsByActivity[activityId].includes(email)) {
        participantsByActivity[activityId].push(email);
      }
      renderActivities();

      const msg = document.getElementById("message");
      msg.classList.remove("hidden");
      msg.textContent = "Signed up successfully!";
      setTimeout(() => msg.classList.add("hidden"), 3000);
      signupForm.reset();
    } catch (err) {
      const msg = document.getElementById("message");
      msg.classList.remove("hidden");
      msg.textContent = "Signup failed.";
      setTimeout(() => msg.classList.add("hidden"), 3000);
      console.error(err);
    }
  }

  signupForm.addEventListener("submit", handleSignup);

  // initial load
  fetchActivitiesAndSignups();
});
