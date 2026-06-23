const insightsCache = {};

async function loadInsights() {
  const weekStart = document.getElementById("weekSelect").value;
  const btn = document.getElementById("insightsBtn");
  const body = document.getElementById("insightsBody");
  const text = document.getElementById("insightsText");
  const meta = document.getElementById("insightsMeta");

  if (insightsCache[weekStart]) {
    text.textContent = insightsCache[weekStart].insight;
    meta.textContent = `Cached · ${insightsCache[weekStart].tokens_used} tokens used`;
    body.style.display = "block";
    return;
  }

  btn.disabled = true;
  btn.textContent = "⟳ Generating...";
  body.style.display = "none";

  try {
    const data = await fetchInsights(weekStart);
    insightsCache[weekStart] = data;
    text.textContent = data.insight;
    meta.textContent = `Generated now · ${data.tokens_used} tokens used`;
    body.style.display = "block";
  } catch (err) {
    text.textContent = "Could not generate insights. Please try again.";
    body.style.display = "block";
  } finally {
    btn.disabled = false;
    btn.textContent = "✦ Generate Insights";
  }
}

let trendChartInstance = null;

function toggleDark() {
  const html = document.documentElement;
  const isDark = html.getAttribute("data-theme") === "dark";
  html.setAttribute("data-theme", isDark ? "light" : "dark");
  localStorage.setItem("focusflow-theme", isDark ? "light" : "dark");
  document.querySelector(".dark-toggle").textContent = isDark
    ? "🌙 Dark Mode"
    : "☀️ Light Mode";
}

const savedTheme = localStorage.getItem("focusflow-theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);
if (savedTheme === "dark") {
  document.querySelector(".dark-toggle").textContent = "☀️ Light Mode";
}

function getScoreClass(score) {
  if (score <= 40) return "score-low";
  if (score <= 70) return "score-mid";
  return "score-high";
}

function getStatusClass(avg) {
  if (avg <= 40) return "status-healthy";
  if (avg <= 70) return "status-atrisk";
  return "status-critical";
}

function getStatusLabel(avg) {
  if (avg <= 40) return "Healthy";
  if (avg <= 70) return "At Risk";
  return "Critical";
}

function getTrendHTML(direction, trend) {
  if (direction === "no_previous_data")
    return '<div class="trend" style="color:var(--text-muted)">First week</div>';
  const arrow =
    direction === "worse" ? "▲" : direction === "better" ? "▼" : "—";
  const cls = `trend-${direction}`;
  const label =
    direction === "worse"
      ? `+${trend} vs last week`
      : direction === "better"
        ? `${trend} vs last week`
        : "Unchanged";
  return `<div class="trend ${cls}">${arrow} ${label}</div>`;
}

function renderHealthSummary(team) {
  const scores = team.map((p) => p.fragmentation_score || 0);
  const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  const statusClass = getStatusClass(avg);
  const statusLabel = getStatusLabel(avg);
  const totalMeetings = team
    .reduce((a, p) => a + p.meeting_hours, 0)
    .toFixed(1);
  const totalInterruptions = team.reduce((a, p) => a + p.interruption_count, 0);
  const totalEmails = team.reduce((a, p) => a + p.email_count, 0);

  const mostDeterioration = team
    .filter((p) => p.trend_direction === "worse")
    .sort((a, b) => b.fragmentation_trend - a.fragmentation_trend)[0];

  const mostImproved = team
    .filter((p) => p.trend_direction === "better")
    .sort((a, b) => a.fragmentation_trend - b.fragmentation_trend)[0];

  const deteriorationHTML = mostDeterioration
    ? `<div class="health-stat">
        <div class="health-stat-label">Most Deteriorated Role</div>
        <div class="health-stat-value" style="font-size:0.85rem">${mostDeterioration.role.split(" ")[0]}</div>
        <div class="health-stat-sub">+${mostDeterioration.fragmentation_trend} pts vs last week</div>
       </div>`
    : "";

  const improvedHTML = mostImproved
    ? `<div class="health-stat">
        <div class="health-stat-label">Most Improved Role</div>
        <div class="health-stat-value" style="font-size:0.85rem">${mostImproved.role.split(" ")[0]}</div>
        <div class="health-stat-sub">${mostImproved.fragmentation_trend} pts vs last week</div>
       </div>`
    : "";

  document.getElementById("healthSummary").innerHTML = `
    <div class="health-header">
      <span class="health-title">Team Health Summary</span>
      <div class="team-status ${statusClass}">
        <div class="status-dot"></div>
        <span class="status-label">${statusLabel}</span>
      </div>
    </div>
    <div class="health-stats">
      <div class="health-stat">
        <div class="health-stat-label">Avg Fragmentation</div>
        <div class="health-stat-value">${avg}<span style="font-size:0.8rem;font-weight:400"> / 100</span></div>
        <div class="health-stat-sub">across ${team.length} team members</div>
      </div>
      <div class="health-stat">
        <div class="health-stat-label">Total Meeting Hours</div>
        <div class="health-stat-value">${totalMeetings}h</div>
        <div class="health-stat-sub">team wide this week</div>
      </div>
      <div class="health-stat">
        <div class="health-stat-label">Total Interruptions</div>
        <div class="health-stat-value">${totalInterruptions}</div>
        <div class="health-stat-sub">across all team members</div>
      </div>
      <div class="health-stat">
        <div class="health-stat-label">Total Emails</div>
        <div class="health-stat-value">${totalEmails}</div>
        <div class="health-stat-sub">across all team members</div>
      </div>
      ${deteriorationHTML}
      ${improvedHTML}
    </div>
  `;
}

function renderTeam(data) {
  const grid = document.getElementById("teamGrid");
  if (!data.team || data.team.length === 0) {
    grid.innerHTML = '<div class="error">No data found for this week.</div>';
    return;
  }
  renderHealthSummary(data.team);
  grid.innerHTML = data.team
    .map(
      (person) => `
      <div class="person-card" onclick="loadTrend(${person.person_id}, '${person.name}')">
        <div class="card-header">
          <div>
            <div class="person-name">${person.name}</div>
            <div class="person-role">${person.role}</div>
          </div>
          <div class="score-block">
            <div class="score-badge ${getScoreClass(person.fragmentation_score)}">
              ${person.fragmentation_score}
            </div>
            ${getTrendHTML(person.trend_direction, person.fragmentation_trend)}
          </div>
        </div>
        <div class="card-stats">
          <div class="stat">
            <div class="stat-label">Meeting Hours</div>
            <div class="stat-value">${person.meeting_hours}h</div>
          </div>
          <div class="stat">
            <div class="stat-label">Emails</div>
            <div class="stat-value">${person.email_count}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Interruptions</div>
            <div class="stat-value">${person.interruption_count}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Focus Hours</div>
            <div class="stat-value">${person.focus_hours}h</div>
          </div>
        </div>
        <div class="click-hint">Click to view 4 week trend →</div>
      </div>
    `,
    )
    .join("");
}

async function loadDashboard() {
  const weekStart = document.getElementById("weekSelect").value;
  document.getElementById("teamGrid").innerHTML =
    '<div class="loading">Loading team data...</div>';
  document.getElementById("healthSummary").innerHTML =
    '<div class="loading">Loading team health...</div>';
  document.getElementById("insightsBody").style.display = "none";
  closeTrend();
  try {
    const data = await fetchDashboard(weekStart);
    renderTeam(data);
  } catch (err) {
    document.getElementById("teamGrid").innerHTML =
      '<div class="error">Could not connect to API. Is Docker running?</div>';
    document.getElementById("healthSummary").innerHTML = "";
  }
}

async function loadTrend(personId, personName) {
  document.getElementById("trendTitle").textContent =
    `${personName} — 4 Week Trend`;
  document.getElementById("trendSection").classList.add("visible");
  document.getElementById("trendTable").innerHTML =
    "<tr><td>Loading...</td></tr>";

  try {
    const data = await fetchPersonTrend(personId);
    const labels = data.weeks.map((w, i) => `Week ${i + 1}`);
    const scores = data.weeks.map((w) => w.fragmentation_score);

    if (trendChartInstance) trendChartInstance.destroy();
    trendChartInstance = new Chart(document.getElementById("trendChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Fragmentation Score",
            data: scores,
            borderColor: "#00b4d8",
            backgroundColor: "rgba(0,180,216,0.1)",
            borderWidth: 2,
            pointRadius: 5,
            pointBackgroundColor: "#00b4d8",
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            min: 0,
            max: 100,
            ticks: { stepSize: 20 },
            grid: { color: "rgba(128,128,128,0.1)" },
          },
          x: { grid: { color: "rgba(128,128,128,0.1)" } },
        },
        plugins: { legend: { display: false } },
      },
    });

    document.getElementById("trendTable").innerHTML = `
      <thead>
        <tr>
          <th>Week</th>
          <th>Score</th>
          <th>Meetings</th>
          <th>Emails</th>
          <th>Interruptions</th>
          <th>Focus Hours</th>
          <th>Capacity</th>
        </tr>
      </thead>
      <tbody>
        ${data.weeks
          .map(
            (w, i) => `
          <tr>
            <td>Week ${i + 1}</td>
            <td><strong>${w.fragmentation_score}</strong></td>
            <td>${w.meeting_hours}h</td>
            <td>${w.email_count}</td>
            <td>${w.interruption_count}</td>
            <td>${w.focus_hours}h</td>
            <td>${w.capacity_hours}h</td>
          </tr>
        `,
          )
          .join("")}
      </tbody>
    `;

    document
      .getElementById("trendSection")
      .scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    document.getElementById("trendTable").innerHTML =
      "<tr><td>Error loading trend data.</td></tr>";
  }
}

function closeTrend() {
  document.getElementById("trendSection").classList.remove("visible");
  if (trendChartInstance) {
    trendChartInstance.destroy();
    trendChartInstance = null;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("weekSelect")
    .addEventListener("change", loadDashboard);
  loadDashboard();
});
