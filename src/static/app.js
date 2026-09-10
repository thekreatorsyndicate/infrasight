const money = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
let projects = [];

const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;" })[char]);
const compact = value => value === null || value === undefined ? "Unavailable" : value;
const currency = value => value === null || value === undefined ? "Unavailable" : money.format(value);
const percent = value => value === null || value === undefined ? "—" : `${Math.round(value * 100)}%`;
const displayName = value => String(value || "Unnamed work").replace(/^WS\/MP\d+\/\d{4}-\d{4}\/\d+-/, "").replace(/^NA-/, "");

function scoreExplanation(project) {
  const evidence = project.evidence || {};
  const checks = ["cost", "expenditure", "duration"];
  const available = checks.filter(check => evidence[check]?.score !== null && evidence[check]?.score !== undefined);
  const missing = checks.filter(check => !available.includes(check));
  const peerSupport = Math.min(100, Math.round((project.peer_count || 0) / 10 * 100));
  const coverage = Math.round(available.length / checks.length * 100);
  const score = project.investigation_priority ?? "—";
  const signalNames = available.map(check => ({ cost: "cost", expenditure: "spend", duration: "duration" })[check]).join(", ") || "no";
  const missingNames = missing.map(check => ({ cost: "cost", expenditure: "spend", duration: "duration" })[check]).join(" and ");
  return `<strong>Why priority is ${score}</strong><p>Priority is weighted average of available signals: ${signalNames}. Each signal measures how far this work differs from comparable peers using median and median absolute deviation; it is capped at 100. Missing checks are excluded, not treated as zero.${missingNames ? ` ${missingNames[0].toUpperCase() + missingNames.slice(1)} check${missing.length > 1 ? "s are" : " is"} unavailable for this record.` : ""}</p><strong>Why confidence is ${Math.round((project.confidence_score || 0) * 100)}%</strong><p>Confidence combines peer support and data coverage. ${project.peer_count || 0} peers provide ${peerSupport}% peer support; ${available.length} of 3 checks provide ${coverage}% data coverage. Here, ${peerSupport}% × ${coverage}% = ${Math.round((project.confidence_score || 0) * 100)}%.</p>`;
}

function renderDetail(project) {
  const evidence = project.evidence || {}, cost = evidence.cost || {}, spend = evidence.expenditure || {}, duration = evidence.duration || {};
  document.querySelector("#detail-name").textContent = displayName(project.work_name);
  document.querySelector("#detail-score").textContent = project.investigation_priority ?? "—";
  document.querySelector("#detail-meta").textContent = `${project.district}, ${project.state} · ${project.peer_count} comparable ${project.peer_group_level} peers · confidence ${Math.round((project.confidence_score || 0) * 100)}%${project.integrity_flags?.length ? ` · ${project.integrity_flags.join(", ").replaceAll("_", " ")}` : ""}`;
  const explanation = document.querySelector("#score-explanation");
  explanation.hidden = false;
  explanation.innerHTML = scoreExplanation(project);
  document.querySelector("#evidence").innerHTML = [
    ["Cost signal", percent(cost.score), `${currency(cost.project_amount)} proposed; peer median ${currency(cost.peer_median)}.`],
    ["Spend signal", percent(spend.score), spend.available === false ? "Unavailable: official snapshot returned no expenditure rows." : `${percent(spend.utilization)} utilised; peer median ${percent(spend.peer_median)}.`],
    ["Duration signal", percent(duration.score), `${compact(duration.days)} days; peer median ${compact(duration.peer_median_days)} days.`],
  ].map(([label, value, text]) => `<article class="signal"><span class="signal-label">${label}</span><strong class="signal-value">${value}</strong><p>${text}</p></article>`).join("");
}

function selectProject(workId, scroll = true) {
  const project = projects.find(item => item.work_id === workId);
  if (!project) return;
  document.querySelectorAll("tr[data-work-id]").forEach(row => row.classList.toggle("selected", row.dataset.workId === workId));
  renderDetail(project);
  if (scroll) document.querySelector("#detail").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
}

function renderRows() {
  const minimum = Number(document.querySelector("#score-filter").value);
  const shown = projects.filter(project => (project.investigation_priority ?? 0) >= minimum);
  const body = document.querySelector("#project-rows");
  body.innerHTML = shown.map(project => `<tr tabindex="0" data-work-id="${escapeHtml(project.work_id)}">
    <td><span class="work-name">${escapeHtml(displayName(project.work_name))}</span><span class="subtle">${escapeHtml(project.work_id)}</span></td>
    <td>${escapeHtml(project.district)}<br><span class="subtle">${escapeHtml(project.state)}</span></td>
    <td>${currency(project.recommended_amount)}</td><td class="priority">${project.investigation_priority ?? "—"}</td>
    <td class="${project.integrity_flags?.length ? "flag" : "clear"}">${project.integrity_flags?.length ? escapeHtml(project.integrity_flags.join(", ").replaceAll("_", " ")) : "No integrity flags"}</td>
  </tr>`).join("") || `<tr><td colspan="5" class="loading">No works match this threshold.</td></tr>`;
  body.querySelectorAll("tr[data-work-id]").forEach(row => {
    const choose = () => selectProject(row.dataset.workId);
    row.addEventListener("click", choose);
    row.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(); } });
  });
}

function renderInsights(insights) {
  document.querySelector("#map-note").textContent = insights.map_note;
  if (insights.map_embed_url) document.querySelector("#coverage-map").src = insights.map_embed_url;
  document.querySelector("#coordinate-coverage").textContent = `${insights.coordinate_coverage}%`;
  document.querySelector("#location-list").innerHTML = insights.state_coverage.map(location => `<div class="location-row"><strong>${escapeHtml(location.state || "Unknown state")}</strong><span>${location.works} saved works</span></div>`).join("");
  document.querySelector("#scored-count").textContent = `${insights.scored_projects}/${projects.length}`;
  document.querySelector("#spend-gap-count").textContent = insights.unavailable_expenditure_signals;
  document.querySelector("#category-list").innerHTML = insights.categories.map(category => `<div class="category-row"><strong>${escapeHtml(category.category)}</strong><span>${category.works} works</span><span>${currency(category.recommended_amount)}</span></div>`).join("");
}

function showView(view) {
  document.querySelectorAll("[data-view-panel]").forEach(panel => { panel.hidden = panel.dataset.viewPanel !== view; });
  document.querySelectorAll("[data-view]").forEach(button => button.classList.toggle("active", button.dataset.view === view));
  if (view !== "explorer") document.querySelector(`[data-view-panel="${view}"]`).scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
}

async function loadSnapshot({ announce = false } = {}) {
  const button = document.querySelector("#fetch-entries"), status = document.querySelector("#snapshot-status");
  const started = Date.now();
  button.disabled = true; button.textContent = "Loading saved entries…";
  document.querySelector("#project-rows").innerHTML = `<tr><td colspan="5" class="loading">Loading saved records…</td></tr>`;
  try {
    const [all, stats, insights] = await Promise.all([fetch("/projects?limit=250").then(res => res.json()), fetch("/stats").then(res => res.json()), fetch("/insights").then(res => res.json())]);
    const remaining = 1000 - (Date.now() - started);
    if (remaining > 0) await new Promise(resolve => setTimeout(resolve, remaining));
    projects = all.items;
    document.querySelector("#project-count").textContent = stats.projects;
    document.querySelector("#priority-count").textContent = stats.investigation_priority_50_plus;
    status.textContent = `${all.count} saved entries loaded${stats.snapshot_id ? ` · ${stats.snapshot_id}` : ""}.`;
    if (stats.source?.source) document.querySelector("#source-note").textContent = `${stats.source.source}. Saved retrieval: ${stats.snapshot_id}. Scores support human review; they do not determine fraud or illegality.`;
    renderRows(); renderInsights(insights);
    if (projects[0]) selectProject(projects[0].work_id, false);
    if (announce) document.querySelector("[data-view-panel=explorer]").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (_) { status.textContent = "Snapshot unavailable. Run scripts/build_live_snapshot.py, then reload."; document.querySelector("#project-rows").innerHTML = `<tr><td colspan="5" class="loading">Saved snapshot unavailable.</td></tr>`; }
  finally { button.disabled = false; button.innerHTML = `Fetch entries <span aria-hidden="true">↓</span>`; }
}

document.querySelector("#score-filter").addEventListener("change", renderRows);
document.querySelector("#fetch-entries").addEventListener("click", () => loadSnapshot({ announce: true }));
document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => showView(button.dataset.view)));
