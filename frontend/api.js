const API =
  window.location.origin === "http://127.0.0.1:5500"
    ? "http://localhost:8000"
    : window.location.origin;

async function fetchDashboard(weekStart) {
  const res = await fetch(`${API}/dashboard/weekly?week_start=${weekStart}`);
  return res.json();
}

async function fetchPersonTrend(personId) {
  const res = await fetch(`${API}/people/${personId}/trend`);
  return res.json();
}

async function fetchInsights(weekStart) {
  const res = await fetch(`${API}/insights/weekly?week_start=${weekStart}`);
  return res.json();
}
