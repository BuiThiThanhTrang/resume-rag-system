import { escapeHtml, safeList } from "../utils/format.js";

function chips(items) {
  return items.length ? items.slice(0, 12).map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("") : '<span class="muted">No data extracted</span>';
}

export function DetailPanel(candidate) {
  if (!candidate) {
    return `
      <aside class="detail-panel">
        <h3>Candidate Detail</h3>
        <p class="muted">Select a candidate card to inspect extracted profile, skills, and resume evidence.</p>
      </aside>
    `;
  }

  const name = candidate.candidate_name || String(candidate.file_name || "Candidate").replace(".pdf", "");
  const experience = safeList(candidate.experience).slice(0, 5);
  const education = safeList(candidate.education).slice(0, 5);
  const evidence = String(candidate.evidence || candidate.summary || "").slice(0, 1200);

  return `
    <aside class="detail-panel">
      <h3>${escapeHtml(name)}</h3>
      <p class="muted">${escapeHtml(candidate.file_name || "")}</p>

      <div class="section-label">Contact</div>
      <p class="muted">Email: ${escapeHtml(candidate.email || "Not found")}</p>
      <p class="muted">Phone: ${escapeHtml(candidate.phone || "Not found")}</p>

      <div class="section-label">Skills</div>
      <div class="chips">${chips(safeList(candidate.skills))}</div>

      <div class="section-label">Experience</div>
      ${experience.length ? experience.map((item) => `<p class="muted">${escapeHtml(item)}</p>`).join("") : '<p class="muted">No experience extracted</p>'}

      <div class="section-label">Education</div>
      ${education.length ? education.map((item) => `<p class="muted">${escapeHtml(item)}</p>`).join("") : '<p class="muted">No education extracted</p>'}

      <div class="section-label">Resume Evidence</div>
      <p class="muted evidence">${escapeHtml(evidence)}</p>
    </aside>
  `;
}
