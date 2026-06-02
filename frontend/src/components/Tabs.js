export function Tabs(activeScreen) {
  const tabs = [
    ["search", "Search"],
    ["candidates", "Candidates"],
    ["analytics", "Analytics"]
  ];
  return `
    <nav class="tabs">
      ${tabs
        .map(([id, label]) => `<button class="tab ${activeScreen === id ? "active" : ""}" data-screen="${id}">${label}</button>`)
        .join("")}
    </nav>
  `;
}
