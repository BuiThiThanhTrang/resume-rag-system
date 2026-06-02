import { domainLabel, escapeHtml } from "../utils/format.js";

export function AnalyticsScreen(state) {
  const domainRows = Object.entries(state.analytics.domain_counts || {})
    .map(([domain, count]) => {
      const total = Math.max(state.analytics.profiles_count || 1, 1);
      const width = Math.round((Number(count) / total) * 100);
      return `
        <div class="domain-row">
          <div><strong>${escapeHtml(domainLabel(domain))}</strong><span>${count}</span></div>
          <div class="progress-track"><div class="progress-fill" style="width:${width}%"></div></div>
        </div>
      `;
    })
    .join("");

  const eventRows = state.events
    .slice()
    .reverse()
    .map(
      (event) => `
        <tr>
          <td>${escapeHtml(event.event_type || "")}</td>
          <td>${escapeHtml(event.status || "")}</td>
          <td>${escapeHtml(event.file_name || "")}</td>
          <td>${escapeHtml(event.domain || "")}</td>
          <td>${escapeHtml(event.wall_seconds ?? "")}</td>
          <td>${escapeHtml(event.peak_memory_mb ?? "")}</td>
        </tr>
      `
    )
    .join("");

  const phoenix = state.analytics.phoenix || {};

  return `
    <section class="analytics-grid">
      <div class="panel">
        <h2>Candidates by Domain</h2>
        ${domainRows || '<p class="muted">No profile distribution yet.</p>'}
      </div>
      <div class="panel">
        <h2>Phoenix</h2>
        <p class="status ${phoenix.initialized ? "ok" : ""}">${phoenix.initialized ? "Enabled" : "Disabled"}</p>
        <p class="muted">Project: ${escapeHtml(phoenix.project_name || "resume-rag-system")}</p>
        <p class="muted">UI: ${escapeHtml(phoenix.ui || "http://localhost:6006")}</p>
      </div>
      <div class="panel wide">
        <h2>Runtime Events</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Status</th>
                <th>File</th>
                <th>Domain</th>
                <th>Wall seconds</th>
                <th>Memory MB</th>
              </tr>
            </thead>
            <tbody>${eventRows || '<tr><td colspan="6">No monitoring events yet.</td></tr>'}</tbody>
          </table>
        </div>
      </div>
    </section>
  `;
}
