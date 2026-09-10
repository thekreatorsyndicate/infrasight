const money = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
let projects = [];

function compact(value) { return value === null || value === undefined ? "Unavailable" : value; }
function currency(value) { return value === null || value === undefined ? "Unavailable" : money.format(value); }
function percent(value) { return value === null || value === undefined ? "—" : `${Math.round(value * 100)}%`; }

function renderDetail(project) {
  const evidence = project.evidence || {};
  const cost = evidence.cost || {}, spend = evidence.expenditure || {}, duration = evidence.duration || {};
  document.querySelector("#detail-name").textContent = project.work_name;
  document.querySelector("#detail-score").textContent = project.investigation_priority ?? "—";
  document.querySelector("#detail-meta").textContent = `${project.district}, ${project.state} · ${project.peer_count} comparable ${project.peer_group_level} peers · confidence ${Math.round((project.confidence_score || 0) * 100)}%${project.integrity_flags?.length ? ` · ${project.integrity_flags.join(", ").replaceAll("_", " ")}` : ""}`;
  document.querySelector("#evidence").innerHTML = [
    ["Cost signal", percent(cost.score), `${currency(cost.project_amount)} proposed; peer median ${currency(cost.peer_median)}.`],
    ["Spend signal", percent(spend.score), spend.available === false ? "Unavailable: official snapshot returned no expenditure rows." : `${percent(spend.utilization)} utilised; peer median ${percent(spend.peer_median)}.`],
    ["Duration signal", percent(duration.score), `${compact(duration.days)} days; peer median ${compact(duration.peer_median_days)} days.`],
  ].map(([label, value, text]) => `<article class="signal"><span class="signal-label">${label}</span><strong class="signal-value">${value}</strong><p>${text}</p></article>`).join("");
}

function renderRows() {
  const minimum = Number(document.querySelector("#score-filter").value);
  const shown = projects.filter(project => (project.investigation_priority ?? 0) >= minimum);
  const body = document.querySelector("#project-rows");
  body.innerHTML = shown.map(project => `<tr tabindex="0" data-work-id="${project.work_id}">
    <td><span class="work-name">${project.work_name}</span><span class="subtle">${project.work_id}</span></td>
    <td>${project.district}<br><span class="subtle">${project.state}</span></td>
    <td>${money.format(project.recommended_amount)}</td>
    <td class="priority">${project.investigation_priority ?? "—"}</td>
    <td class="${project.integrity_flags?.length ? "flag" : "clear"}">${project.integrity_flags?.length ? project.integrity_flags.join(", ").replaceAll("_", " ") : "No integrity flags"}</td>
  </tr>`).join("") || `<tr><td colspan="5" class="loading">No works match this threshold.</td></tr>`;
  body.querySelectorAll("tr[data-work-id]").forEach(row => {
    const choose = () => { body.querySelectorAll("tr").forEach(item => item.classList.remove("selected")); row.classList.add("selected"); renderDetail(projects.find(project => project.work_id === row.dataset.workId)); document.querySelector("#detail").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" }); };
    row.addEventListener("click", choose); row.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(); } });
  });
}

async function boot() {
  try {
    const [all, stats] = await Promise.all([fetch("/projects").then(res => res.json()), fetch("/stats").then(res => res.json())]);
    projects = all.items;
    document.querySelector("#project-count").textContent = stats.projects;
    document.querySelector("#priority-count").textContent = stats.investigation_priority_50_plus;
    if (stats.source?.source) document.querySelector("#source-note").textContent = `${stats.source.source}. Static retrieval: ${stats.snapshot_id}. Flagged for human review; this system does not determine fraud or illegality.`;
    renderRows();
    const initial = projects[0];
    if (initial) { renderDetail(initial); document.querySelector('[data-work-id="' + initial.work_id + '"]')?.classList.add("selected"); }
  } catch (_) { document.querySelector("#project-rows").innerHTML = `<tr><td colspan="5" class="loading">Demo data unavailable. Run <code>python scripts/build_demo.py</code>, then refresh.</td></tr>`; }
}
document.querySelector("#score-filter").addEventListener("change", renderRows);
boot();
