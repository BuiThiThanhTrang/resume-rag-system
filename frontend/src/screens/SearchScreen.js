import { api } from "../api/client.js";
import { CandidateCard } from "../components/CandidateCard.js";
import { DetailPanel } from "../components/DetailPanel.js";

function loadProfileFromSource(source) {
  const metadata = source.metadata || {};
  const extractedProfile = source.profile || {};
  return {
    ...extractedProfile,
    file_name: metadata.file_name || "Unknown resume",
    domain: metadata.domain || "Unknown",
    summary: extractedProfile.summary || String(source.text || "").slice(0, 900),
    evidence: source.text || "",
    raw_score: Number(source.score || 0)
  };
}

function buildCandidateResults(sources) {
  const maxScore = Math.max(...sources.map((source) => Number(source.score || 0)), 0.0001);
  return sources.map((source) => {
    const profile = loadProfileFromSource(source);
    const relative = Number(source.score || 0) / maxScore;
    return { ...profile, match_score: Math.max(42, Math.min(98, Math.round(relative * 92))) };
  });
}

export function SearchScreen(state) {
  const cards = state.candidates.length
    ? state.candidates.map((candidate, index) => CandidateCard(candidate, index)).join("")
    : '<div class="empty">Search for candidates after building the index. Try: Find banking candidates with credit risk experience.</div>';

  return `
    <section class="search-layout">
      <div>
        <form id="searchForm" class="search-form">
          <input id="queryInput" type="search" placeholder="Find IT candidates with SQL, Python, and data analysis experience" />
          <button class="primary" type="submit">Search</button>
        </form>
        <h2>Results</h2>
        <div class="results-list">${cards}</div>
      </div>
      ${DetailPanel(state.selectedCandidate)}
    </section>
  `;
}

export function bindSearchScreen(state, render) {
  document.querySelector("#searchForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.querySelector("#queryInput")?.value.trim();
    if (!query) return;
    state.loading = true;
    state.message = "Searching candidate evidence...";
    render();
    try {
      const response = await api.search({ query, top_k: state.filters.topK });
      state.candidates = buildCandidateResults(response.sources || []);
      state.selectedCandidate = state.candidates[0] || null;
      state.message = state.candidates.length ? `Found ${state.candidates.length} candidate matches.` : "No matching candidates found.";
    } catch (error) {
      state.message = error.message;
    } finally {
      state.loading = false;
      render();
    }
  });

  document.querySelectorAll("[data-view-candidate]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedCandidate = state.candidates[Number(button.dataset.viewCandidate)];
      render();
    });
  });
}
