const API_URL = "https://hazm-tuwaiq.onrender.com/incidents";

async function loadIncidents() {
  const res = await fetch(API_URL);
  const data = await res.json();
  document.getElementById("output").textContent =
    JSON.stringify(data, null, 2);
}
