import { escapeHtml } from "../utils/format.js";

export function MetricCard({ label, value, caption = "" }) {
  return `
    <section class="metric-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(caption)}</small>
    </section>
  `;
}
