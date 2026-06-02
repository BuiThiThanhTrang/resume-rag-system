import { domainLabel, modeLabel } from "../utils/format.js";

export function Sidebar(state) {
  return `
    <aside class="sidebar">
      <div class="sidebar-title">Filters</div>
      <label class="field-label">Domains</label>
      <div class="check-list">
        ${state.config.domains
          .map(
            (domain) => `
              <label class="check-row">
                <input type="checkbox" data-domain="${domain}" ${state.filters.domains.includes(domain) ? "checked" : ""} />
                <span>${domainLabel(domain)}</span>
              </label>
            `
          )
          .join("")}
      </div>

      <label class="field-label" for="extractionMode">Extraction</label>
      <select id="extractionMode">
        ${state.config.extraction_modes
          .map((mode) => `<option value="${mode}" ${state.filters.extractionMode === mode ? "selected" : ""}>${modeLabel(mode)}</option>`)
          .join("")}
      </select>

      <label class="field-label" for="maxFiles">Files per domain</label>
      <input id="maxFiles" type="number" min="1" max="500" value="${state.filters.maxFilesPerDomain}" />

      <label class="field-label" for="topK">Results</label>
      <input id="topK" type="number" min="1" max="10" value="${state.filters.topK}" />

      <label class="check-row toggle-row">
        <input id="darkMode" type="checkbox" ${state.filters.darkMode ? "checked" : ""} />
        <span>Dark mode</span>
      </label>

      <button id="buildIndex" class="primary full">Build / rebuild index</button>

      <div class="sidebar-title small">Dataset Overview</div>
      <div class="side-metric"><span>Resumes Indexed</span><strong>${state.analytics.profiles_count}</strong></div>
      <div class="side-metric"><span>Retrieval</span><strong>TF-IDF</strong></div>
      <div class="side-metric"><span>Avg Search</span><strong>${state.analytics.avg_search_seconds || 0}s</strong></div>
    </aside>
  `;
}
