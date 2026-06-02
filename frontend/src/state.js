export const state = {
  config: {
    domains: ["BANKING", "INFORMATION-TECHNOLOGY"],
    extraction_modes: ["rule_based", "openai", "langchain_openai"],
    default_max_files_per_domain: 50
  },
  filters: {
    domains: ["BANKING", "INFORMATION-TECHNOLOGY"],
    extractionMode: "rule_based",
    maxFilesPerDomain: 20,
    topK: 5,
    darkMode: false
  },
  analytics: {
    profiles_count: 0,
    domain_counts: {},
    avg_search_seconds: 0,
    avg_extract_seconds: 0,
    phoenix: {}
  },
  profiles: [],
  events: [],
  candidates: [],
  selectedCandidate: null,
  activeScreen: "search",
  loading: false,
  message: ""
};
