export function domainLabel(domain) {
  return {
    "INFORMATION-TECHNOLOGY": "Information Technology",
    BANKING: "Banking"
  }[domain] || domain;
}

export function modeLabel(mode) {
  return {
    rule_based: "Rule-based",
    openai: "OpenAI SDK",
    langchain_openai: "LangChain + OpenAI"
  }[mode] || mode;
}

export function matchColor(score) {
  if (score >= 90) return "#16A34A";
  if (score >= 70) return "#2563EB";
  if (score >= 50) return "#F97316";
  return "#64748B";
}

export function safeList(value) {
  if (Array.isArray(value)) return value.filter(Boolean).map(String);
  if (typeof value === "string" && value.trim()) return [value];
  return [];
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
