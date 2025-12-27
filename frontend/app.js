const API = "https://hazm-tuwaiq.onrender.com";

async function loadIncidents() {
  const res = await fetch(`${API}/incidents`);
  const data = await res.json();

  const list = document.getElementById("incidentList");
  list.innerHTML = "";

  data.forEach(i => {
    const li = document.createElement("li");
    li.textContent = `${i.title} – ${i.severity}`;
    list.appendChild(li);
  });
}

async function createIncident() {
  const body = {
    title: document.getElementById("title").value,
    location: document.getElementById("location").value,
    severity: document.getElementById("severity").value
  };

  await fetch(`${API}/incidents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  loadIncidents();
}

loadIncidents();
