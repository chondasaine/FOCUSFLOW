const API = "http://localhost:8000";

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
