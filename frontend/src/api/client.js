const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  health: () => request("/health"),
  config: () => request("/config"),
  analytics: () => request("/analytics"),
  events: () => request("/events"),
  clearEvents: () => request("/events", { method: "DELETE" }),
  profiles: (domain = "All") => request(`/profiles?domain=${encodeURIComponent(domain)}`),
  ingest: (payload) => request("/ingest", { method: "POST", body: JSON.stringify(payload) }),
  search: (payload) => request("/search", { method: "POST", body: JSON.stringify(payload) })
};
