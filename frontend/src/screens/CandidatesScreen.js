import { domainLabel, escapeHtml, safeList } from "../utils/format.js";

export function CandidatesScreen(state) {
  const rows = state.profiles
    .map(
      (profile) => `
        <tr>
          <td>${escapeHtml(profile.candidate_name || String(profile.file_name || "").replace(".pdf", ""))}</td>
          <td>${escapeHtml(profile.file_name || "")}</td>
          <td>${escapeHtml(domainLabel(profile.domain || ""))}</td>
          <td>${escapeHtml(profile.email || "")}</td>
          <td>${escapeHtml(profile.phone || "")}</td>
          <td>${escapeHtml(safeList(profile.skills).slice(0, 5).join(", "))}</td>
          <td>${escapeHtml(profile.actual_extraction_engine || "")}</td>
        </tr>
      `
    )
    .join("");

  return `
    <section class="panel">
      <div class="panel-head">
        <h2>Candidates</h2>
        <select id="candidateDomain">
          <option value="All">All domains</option>
          ${state.config.domains.map((domain) => `<option value="${domain}">${domainLabel(domain)}</option>`).join("")}
        </select>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Resume</th>
              <th>Domain</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Skills</th>
              <th>Engine</th>
            </tr>
          </thead>
          <tbody>${rows || '<tr><td colspan="7">No extracted profiles yet. Build the index first.</td></tr>'}</tbody>
        </table>
      </div>
    </section>
  `;
}
