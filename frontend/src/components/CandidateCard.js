import { domainLabel, escapeHtml, matchColor, safeList } from "../utils/format.js";

function inferRole(candidate) {
  const summary = String(candidate.summary || "");
  const firstSentence = summary.split(".")[0]?.trim();
  if (firstSentence && firstSentence.length >= 8 && firstSentence.length <= 95) return firstSentence;
  return `${domainLabel(candidate.domain)} Candidate`;
}

export function CandidateCard(candidate, index) {
  const name = candidate.candidate_name || String(candidate.file_name || "Candidate").replace(".pdf", "");
  const score = Number(candidate.match_score || 0);
  const color = matchColor(score);
  const skills = safeList(candidate.skills).slice(0, 7);
  return `
    <article class="candidate-card">
      <div class="candidate-head">
        <div>
          <h3>${escapeHtml(name)}</h3>
          <p>${escapeHtml(inferRole(candidate))}</p>
        </div>
        <span class="match-pill" style="background:${color}">${score}% Match</span>
      </div>
      <div class="section-label">Skills</div>
      <div class="chips">
        ${skills.length ? skills.map((skill) => `<span class="chip">${escapeHtml(skill)}</span>`).join("") : '<span class="muted">No skills extracted yet</span>'}
      </div>
      <div class="candidate-meta">
        <span>Domain: ${escapeHtml(domainLabel(candidate.domain))}</span>
        <span>Resume: ${escapeHtml(candidate.file_name)}</span>
        <span>Engine: ${escapeHtml(candidate.actual_extraction_engine || "unknown")}</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:${Math.max(4, Math.min(score, 100))}%; background:${color}"></div></div>
      <button class="secondary" data-view-candidate="${index}">View Profile</button>
    </article>
  `;
}
