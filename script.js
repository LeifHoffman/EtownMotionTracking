// =============================================================
//  script.js  –  Page rendering & chart drawing
//  Reads from data.js stubs; swap DB_* arrays for fetch() calls
//  when MariaDB integration is ready.
// =============================================================

// ── UTILITIES ─────────────────────────────────────────────────
function isPositive(str) { return str.startsWith("+"); }

function drawLineChart(ctx, data, labels, minY, maxY) {
  const canvas = ctx.canvas;
  const width  = canvas.width;
  const height = canvas.height;
  const pad    = 40;
  const cw     = width  - pad * 2;
  const ch     = height - pad * 2;
  ctx.clearRect(0, 0, width, height);
  const xStep  = cw / (data.length - 1);
  const yRange = maxY - minY;
  const yScale = ch / yRange;

  ctx.strokeStyle = "#f0f0f0";
  ctx.lineWidth   = 1;
  for (let i = 0; i <= 5; i++) {
    const y = pad + (ch / 5) * i;
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(width - pad, y); ctx.stroke();
  }
  ctx.fillStyle  = "#999";
  ctx.font       = "11px sans-serif";
  ctx.textAlign  = "right";
  for (let i = 0; i <= 5; i++) {
    const val = maxY - (yRange / 5) * i;
    const y   = pad  + (ch / 5) * i;
    ctx.fillText(val.toFixed(1), pad - 8, y + 4);
  }
  ctx.textAlign = "center";
  labels.forEach((lbl, i) => {
    if (i % 2 === 0) ctx.fillText(lbl, pad + xStep * i, height - 10);
  });
  ctx.strokeStyle = "#1d1d1f";
  ctx.lineWidth   = 2;
  ctx.beginPath();
  data.forEach((v, i) => {
    const x = pad + xStep * i;
    const y = pad + ch - (v - minY) * yScale;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#1d1d1f";
  data.forEach((v, i) => {
    const x = pad + xStep * i;
    const y = pad + ch - (v - minY) * yScale;
    ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
  });
}

function resizeAndDraw(entries) {
  entries.forEach(({ target }) => {
    const canvas = target;
    canvas.width  = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    if (canvas.id === "jumpChart")        drawLineChart(canvas.getContext("2d"), DB_AVG_JUMP_HISTORY,                       DB_MONTHLY_LABELS, 13, 19);
    else if (canvas.id === "dashChart")   drawLineChart(canvas.getContext("2d"), DB_AVG_DASH_HISTORY,                       DB_MONTHLY_LABELS, 4.2, 4.5);
    else if (canvas.id === "athleteJumpChart") {
      const a = currentAthlete();
      drawLineChart(canvas.getContext("2d"), a.jumpHistory, DB_MONTHLY_LABELS, 12, a.prJump + 2);
    }
  });
}

const ro = new ResizeObserver(resizeAndDraw);

function initCanvas(id) {
  const c = document.getElementById(id);
  if (!c) return null;
  c.width  = c.parentElement.clientWidth;
  c.height = c.parentElement.clientHeight;
  ro.observe(c);
  return c.getContext("2d");
}

// ── INDEX PAGE ────────────────────────────────────────────────
function renderDashboard() {
  const grid = document.getElementById("metricsGrid");
  if (!grid) return;

  // Metric cards
  DB_DASHBOARD_METRICS.forEach(m => {
    grid.innerHTML += `
      <div class="metric-card">
        <div class="metric-label">${m.label}</div>
        <div class="metric-value">${m.value}</div>
        <div class="metric-change${m.negative ? " negative" : ""}">${m.change}</div>
      </div>`;
  });

  // Top performers list
  const list = document.getElementById("topPerformersList");
  if (list) {
    const sorted = [...DB_ATHLETES].sort((a, b) => b.prJump - a.prJump).slice(0, 5);
    sorted.forEach(a => {
      list.innerHTML += `
        <li class="performer-item">
          <div class="performer-avatar"></div>
          <div class="performer-info">
            <div class="performer-name">${a.name.split(" ")[0]} – ${a.prJump} in</div>
            <div class="performer-email">${a.email}</div>
          </div>
        </li>`;
    });
  }

  // Team tables
  const jumpBody = document.getElementById("jumpTotalsBody");
  if (jumpBody) DB_JUMP_TOTALS.forEach(r => {
    jumpBody.innerHTML += `<tr><td>${r.team}</td><td>${r.sessions}</td>
      <td class="${isPositive(r.change) ? "change-positive" : "change-negative"}">${r.change}</td></tr>`;
  });

  const dashBody = document.getElementById("dashTotalsBody");
  if (dashBody) DB_DASH_TOTALS.forEach(r => {
    dashBody.innerHTML += `<tr><td>${r.team}</td><td>${r.sessions}</td>
      <td class="${isPositive(r.change) ? "change-positive" : "change-negative"}">${r.change}</td></tr>`;
  });

  // Charts
  const jCtx = initCanvas("jumpChart");
  const dCtx = initCanvas("dashChart");
  if (jCtx) drawLineChart(jCtx, DB_AVG_JUMP_HISTORY, DB_MONTHLY_LABELS, 13, 19);
  if (dCtx) drawLineChart(dCtx, DB_AVG_DASH_HISTORY, DB_MONTHLY_LABELS, 4.2, 4.5);
}

// ── RECORDING PAGE ────────────────────────────────────────────
function renderRecording() {
  const logBody = document.getElementById("sessionLogBody");
  if (!logBody) return;

  DB_SESSION_LOG.forEach(r => {
    logBody.innerHTML += `<tr><td>${r.source}</td><td>${r.team}</td><td>${r.type}</td></tr>`;
  });

  // Bar chart
  const barChart = document.getElementById("sessionBarChart");
  if (barChart) {
    const maxH = Math.max(...DB_SESSION_REPS.map(r => r.height));
    DB_SESSION_REPS.forEach(r => {
      const pct = (r.height / maxH * 100).toFixed(1);
      barChart.innerHTML += `
        <div class="bar-group">
          <div class="bar" style="height:${pct}%" title="${r.height} in"></div>
          <div class="bar-label">${r.rep}</div>
        </div>`;
    });
  }

  // Live metric simulation (replace with WebSocket/SSE in production)
  let tick = 0;
  const liveJump    = document.getElementById("liveJumpHeight");
  const liveContact = document.getElementById("liveContactTime");
  if (liveJump && liveContact) {
    setInterval(() => {
      const h = (17 + Math.random() * 3).toFixed(1);
      const c = (280 + Math.random() * 60).toFixed(0);
      liveJump.textContent    = `Live Jump: ${h} in`;
      liveContact.textContent = `Contact Time: ${c} ms`;
      tick++;
    }, 2000);
  }

  // Playback controls (stub)
  const btn = document.getElementById("playPauseBtn");
  let playing = false;
  if (btn) btn.addEventListener("click", () => {
    playing = !playing;
    btn.textContent = playing ? "⏸ Pause" : "▶ Play";
  });

  const flagBtn = document.getElementById("flagBtn");
  if (flagBtn) flagBtn.addEventListener("click", () => {
    const scrubber = document.getElementById("scrubber");
    alert(`Rep flagged at ${scrubber ? scrubber.value : 0}% of session`);
  });
}

// ── REPORTS PAGE ──────────────────────────────────────────────
let _currentAthleteId = 1;
function currentAthlete() {
  return DB_ATHLETES.find(a => a.id === _currentAthleteId) || DB_ATHLETES[0];
}

function renderReports() {
  if (!document.getElementById("athleteDetails")) return;
  populateAthleteReport(currentAthlete());

  const jCtx = initCanvas("athleteJumpChart");
  const a    = currentAthlete();
  if (jCtx) drawLineChart(jCtx, a.jumpHistory, DB_MONTHLY_LABELS, 12, a.prJump + 2);
}

function populateAthleteReport(a) {
  document.getElementById("prJumpValue").textContent = a.prJump;
  document.getElementById("prJumpRank").textContent  = a.prJumpRank;
  document.getElementById("prDashValue").textContent = a.prDash;
  document.getElementById("prDashRank").textContent  = a.prDashRank;
  document.getElementById("athleteName").textContent = a.name;
  document.getElementById("athleteJersey").innerHTML = `${a.jersey} <span>BLUE JAYS</span>`;

  document.getElementById("athleteDetails").innerHTML = `
    <div class="ir-detail-row"><span class="ir-detail-label">Team:</span>   <span class="ir-detail-value">${a.team}</span></div>
    <div class="ir-detail-row"><span class="ir-detail-label">Year:</span>   <span class="ir-detail-value">${a.year}</span></div>
    <div class="ir-detail-row"><span class="ir-detail-label">Height:</span> <span class="ir-detail-value">${a.height}</span></div>
    <div class="ir-detail-row"><span class="ir-detail-label">Weight:</span> <span class="ir-detail-value">${a.weight}</span></div>
    <div class="ir-detail-row"><span class="ir-detail-label">Major:</span>  <span class="ir-detail-value">${a.major}</span></div>`;

  const tbody = document.getElementById("recentTestsBody");
  tbody.innerHTML = "";
  a.recentTests.forEach(t => {
    const arrow = t.change === "up"
      ? `<span class="ir-arrow ir-arrow-up">↑</span>`
      : `<span class="ir-arrow ir-arrow-down">↓</span>`;
    tbody.innerHTML += `<tr><td>${t.date}</td><td>${t.type}</td><td>${arrow}</td></tr>`;
  });

  // Redraw chart for new athlete
  const canvas = document.getElementById("athleteJumpChart");
  if (canvas) {
    canvas.width  = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    drawLineChart(canvas.getContext("2d"), a.jumpHistory, DB_MONTHLY_LABELS, 12, a.prJump + 2);
  }
}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  renderDashboard();
  renderRecording();
  renderReports();
});
