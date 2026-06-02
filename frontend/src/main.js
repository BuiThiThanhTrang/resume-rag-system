import { api } from "./api/client.js";
import { Header } from "./components/Header.js";
import { MetricCard } from "./components/MetricCard.js";
import { Sidebar } from "./components/Sidebar.js";
import { Tabs } from "./components/Tabs.js";
import { AnalyticsScreen } from "./screens/AnalyticsScreen.js";
import { CandidatesScreen } from "./screens/CandidatesScreen.js";
import { bindSearchScreen, SearchScreen } from "./screens/SearchScreen.js";
import { state } from "./state.js";
import { modeLabel } from "./utils/format.js";

const app = document.querySelector("#app");

function activeScreenMarkup() {
  if (state.activeScreen === "candidates") return CandidatesScreen(state);
  if (state.activeScreen === "analytics") return AnalyticsScreen(state);
  return SearchScreen(state);
}

function render() {
  document.body.classList.toggle("dark", state.filters.darkMode);
  app.innerHTML = `
    <div class="app-shell">
      ${Sidebar(state)}
      <main class="main">
        ${Header()}
        <section class="metrics-grid">
          ${MetricCard({ label: "Indexed CVs", value: String(state.analytics.profiles_count || 0), caption: "Generated candidate profiles" })}
          ${MetricCard({ label: "Avg Search", value: `${state.analytics.avg_search_seconds || 0}s`, caption: "Measured from local logs" })}
          ${MetricCard({ label: "Domains", value: String(Object.keys(state.analytics.domain_counts || {}).length || state.config.domains.length), caption: "Banking and IT" })}
          ${MetricCard({ label: "Extraction", value: modeLabel(state.filters.extractionMode), caption: "Selected engine" })}
        </section>
        ${Tabs(state.activeScreen)}
        ${state.message ? `<div class="message ${state.loading ? "loading" : ""}">${state.message}</div>` : ""}
        ${activeScreenMarkup()}
      </main>
    </div>
  `;
  bindCommonEvents();
  if (state.activeScreen === "search") bindSearchScreen(state, render);
}

async function refreshData() {
  const [analytics, profiles, events] = await Promise.all([api.analytics(), api.profiles(), api.events()]);
  state.analytics = analytics;
  state.profiles = profiles.profiles || [];
  state.events = events.events || [];
}

function bindCommonEvents() {
  document.querySelectorAll("[data-screen]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.activeScreen = button.dataset.screen;
      if (state.activeScreen !== "search") await refreshData();
      render();
    });
  });

  document.querySelectorAll("[data-domain]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const domain = checkbox.dataset.domain;
      if (checkbox.checked) {
        state.filters.domains = [...new Set([...state.filters.domains, domain])];
      } else {
        state.filters.domains = state.filters.domains.filter((item) => item !== domain);
      }
    });
  });

  document.querySelector("#extractionMode")?.addEventListener("change", (event) => {
    state.filters.extractionMode = event.target.value;
    render();
  });

  document.querySelector("#maxFiles")?.addEventListener("change", (event) => {
    state.filters.maxFilesPerDomain = Number(event.target.value || 20);
  });

  document.querySelector("#topK")?.addEventListener("change", (event) => {
    state.filters.topK = Number(event.target.value || 5);
  });

  document.querySelector("#darkMode")?.addEventListener("change", (event) => {
    state.filters.darkMode = event.target.checked;
    render();
  });

  document.querySelector("#buildIndex")?.addEventListener("click", async () => {
    state.loading = true;
    state.message = "Reading PDFs, extracting profiles, and rebuilding the search index...";
    render();
    try {
      const stats = await api.ingest({
        domains: state.filters.domains,
        extraction_mode: state.filters.extractionMode,
        max_files_per_domain: state.filters.maxFilesPerDomain
      });
      await refreshData();
      state.message = `Indexed ${stats.processed} resumes and ${stats.chunks} chunks.`;
    } catch (error) {
      state.message = error.message;
    } finally {
      state.loading = false;
      render();
    }
  });

  document.querySelector("#candidateDomain")?.addEventListener("change", async (event) => {
    const response = await api.profiles(event.target.value);
    state.profiles = response.profiles || [];
    render();
  });
}

async function bootstrap() {
  try {
    const config = await api.config();
    state.config = config;
    state.filters.domains = [...config.domains];
    state.filters.maxFilesPerDomain = Math.min(config.default_max_files_per_domain || 20, 20);
    await refreshData();
  } catch (error) {
    state.message = `API is not ready: ${error.message}`;
  }
  render();
}

bootstrap();
