import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.env_loader import load_project_env

load_project_env(ROOT_DIR)

from config import ALLOWED_DOMAINS, DEFAULT_MAX_FILES_PER_DOMAIN, EXTRACTION_MODES
from services.rag_service import ResumeRagService
from utils.file_utils import read_json


st.set_page_config(page_title="Resume Intelligence Platform", layout="wide")


def apply_theme(dark_mode: bool) -> None:
    if dark_mode:
        colors = {
            "bg": "#0F172A",
            "panel": "#111827",
            "card": "#1E293B",
            "border": "#334155",
            "text": "#F8FAFC",
            "muted": "#CBD5E1",
            "soft": "#172033",
            "primary": "#60A5FA",
            "secondary": "#93C5FD",
        }
    else:
        colors = {
            "bg": "#F8FAFC",
            "panel": "#FFFFFF",
            "card": "#FFFFFF",
            "border": "#E2E8F0",
            "text": "#0F172A",
            "muted": "#64748B",
            "soft": "#EFF6FF",
            "primary": "#2563EB",
            "secondary": "#3B82F6",
        }

    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {colors["bg"]};
            --app-panel: {colors["panel"]};
            --app-card: {colors["card"]};
            --app-border: {colors["border"]};
            --app-text: {colors["text"]};
            --app-muted: {colors["muted"]};
            --app-soft: {colors["soft"]};
            --app-primary: {colors["primary"]};
            --app-secondary: {colors["secondary"]};
        }}

        .stApp {{
            background: var(--app-bg);
            color: var(--app-text);
        }}

        [data-testid="stSidebar"] {{
            background: var(--app-panel);
            border-right: 1px solid var(--app-border);
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.75rem;
        }}

        .block-container {{
            padding-top: 1.5rem;
            max-width: 1320px;
        }}

        .hero {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 22px;
            border: 1px solid var(--app-border);
            border-radius: 8px;
            background: var(--app-card);
            margin-bottom: 18px;
        }}

        .hero-title {{
            margin: 0;
            color: var(--app-text);
            font-size: 28px;
            font-weight: 760;
            letter-spacing: 0;
        }}

        .hero-subtitle {{
            margin-top: 4px;
            color: var(--app-muted);
            font-size: 14px;
        }}

        .avatar {{
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: var(--app-soft);
            color: var(--app-primary);
            font-weight: 700;
            border: 1px solid var(--app-border);
        }}

        .metric-card {{
            padding: 16px;
            border: 1px solid var(--app-border);
            border-radius: 8px;
            background: var(--app-card);
        }}

        .metric-label {{
            color: var(--app-muted);
            font-size: 12px;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: .04em;
        }}

        .metric-value {{
            color: var(--app-text);
            font-size: 24px;
            font-weight: 760;
            margin-top: 6px;
        }}

        .candidate-card {{
            border: 1px solid var(--app-border);
            border-radius: 8px;
            background: var(--app-card);
            padding: 16px;
            margin-bottom: 12px;
        }}

        .candidate-head {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
        }}

        .candidate-name {{
            color: var(--app-text);
            font-weight: 760;
            font-size: 18px;
        }}

        .candidate-role {{
            color: var(--app-muted);
            font-size: 13px;
            margin-top: 3px;
        }}

        .match-pill {{
            color: white;
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: 760;
            white-space: nowrap;
        }}

        .chip {{
            display: inline-block;
            padding: 4px 8px;
            margin: 4px 5px 0 0;
            border-radius: 999px;
            background: var(--app-soft);
            color: var(--app-primary);
            font-size: 12px;
            font-weight: 650;
        }}

        .candidate-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 12px;
            color: var(--app-muted);
            font-size: 13px;
        }}

        .detail-panel {{
            position: sticky;
            top: 16px;
            border: 1px solid var(--app-border);
            border-radius: 8px;
            background: var(--app-card);
            padding: 18px;
        }}

        .section-title {{
            color: var(--app-text);
            font-size: 13px;
            font-weight: 760;
            margin-top: 16px;
            margin-bottom: 6px;
        }}

        .muted {{
            color: var(--app-muted);
        }}

        .domain-bar {{
            height: 10px;
            border-radius: 999px;
            background: var(--app-soft);
            overflow: hidden;
            margin: 6px 0 12px 0;
        }}

        .domain-fill {{
            height: 10px;
            background: var(--app-primary);
            border-radius: 999px;
        }}

        .stTextInput > div > div > input {{
            border-radius: 8px;
            min-height: 48px;
            font-size: 15px;
        }}

        .stButton > button {{
            border-radius: 8px;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def domain_label(domain: str) -> str:
    return {
        "INFORMATION-TECHNOLOGY": "Information Technology",
        "BANKING": "Banking",
    }.get(domain, domain.title())


def mode_label(mode: str) -> str:
    return {
        "rule_based": "Rule-based (offline)",
        "openai": "OpenAI SDK",
        "langchain_openai": "LangChain + OpenAI",
    }[mode]


def match_color(score: int) -> str:
    if score >= 90:
        return "#16A34A"
    if score >= 70:
        return "#2563EB"
    if score >= 50:
        return "#F97316"
    return "#64748B"


def metric_card(label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def load_profile_from_source(source: Dict[str, Any]) -> Dict[str, Any]:
    metadata = source.get("metadata", {})
    profile: Dict[str, Any] = {}
    json_path = metadata.get("json_path")
    if json_path and Path(json_path).exists():
        try:
            profile = read_json(Path(json_path))
        except Exception:
            profile = {}

    profile.setdefault("file_name", metadata.get("file_name", "Unknown resume"))
    profile.setdefault("domain", metadata.get("domain", "Unknown"))
    profile.setdefault("summary", source.get("text", "")[:900])
    profile["evidence"] = source.get("text", "")
    profile["raw_score"] = float(source.get("score", 0.0))
    return profile


def build_candidate_results(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not sources:
        return []
    max_score = max(float(source.get("score", 0.0)) for source in sources) or 1.0
    results = []
    for source in sources:
        profile = load_profile_from_source(source)
        relative = float(source.get("score", 0.0)) / max_score
        profile["match_score"] = max(42, min(98, round(relative * 92)))
        results.append(profile)
    return results


def infer_role(profile: Dict[str, Any]) -> str:
    summary = str(profile.get("summary") or "")
    if summary:
        first_sentence = summary.split(".")[0].strip()
        if 8 <= len(first_sentence) <= 90:
            return first_sentence
    return f"{domain_label(str(profile.get('domain', '')))} Candidate"


def render_candidate_card(profile: Dict[str, Any], index: int) -> None:
    name = profile.get("candidate_name") or Path(str(profile.get("file_name", "Candidate"))).stem
    role = infer_role(profile)
    domain = domain_label(str(profile.get("domain", "")))
    score = int(profile.get("match_score", 0))
    color = match_color(score)
    skills = safe_list(profile.get("skills"))[:7]
    chips = "".join(f'<span class="chip">{skill}</span>' for skill in skills) or '<span class="muted">No skills extracted yet</span>'
    progress_width = max(4, min(score, 100))

    st.markdown(
        f"""
        <div class="candidate-card">
            <div class="candidate-head">
                <div>
                    <div class="candidate-name">{name}</div>
                    <div class="candidate-role">{role}</div>
                </div>
                <div class="match-pill" style="background:{color};">{score}% Match</div>
            </div>
            <div class="section-title">Skills</div>
            <div>{chips}</div>
            <div class="candidate-meta">
                <span>Domain: {domain}</span>
                <span>Resume: {profile.get("file_name")}</span>
                <span>Engine: {profile.get("actual_extraction_engine", "unknown")}</span>
            </div>
            <div class="domain-bar">
                <div class="domain-fill" style="width:{progress_width}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View profile", key=f"view_profile_{index}_{profile.get('file_name')}"):
        st.session_state["selected_candidate"] = profile


def render_candidate_detail(profile: Dict[str, Any] | None) -> None:
    if not profile:
        st.markdown(
            """
            <div class="detail-panel">
                <div class="candidate-name">Candidate Detail</div>
                <p class="muted">Select a candidate card to inspect extracted profile, skills, and resume evidence.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    name = profile.get("candidate_name") or Path(str(profile.get("file_name", "Candidate"))).stem
    skills = safe_list(profile.get("skills"))
    education = safe_list(profile.get("education"))
    experience = safe_list(profile.get("experience"))
    evidence = str(profile.get("evidence") or profile.get("summary") or "")[:1200]
    skills_html = "".join(f'<span class="chip">{skill}</span>' for skill in skills[:12]) or '<span class="muted">No skills extracted</span>'
    education_html = "<br>".join(education[:5]) or '<span class="muted">No education extracted</span>'
    experience_html = "<br>".join(experience[:5]) or '<span class="muted">No experience extracted</span>'

    st.markdown(
        f"""
        <div class="detail-panel">
            <div class="candidate-name">{name}</div>
            <div class="candidate-role">{infer_role(profile)}</div>
            <div class="section-title">Contact</div>
            <div class="muted">Email: {profile.get("email") or "Not found"}</div>
            <div class="muted">Phone: {profile.get("phone") or "Not found"}</div>
            <div class="section-title">Skills</div>
            <div>{skills_html}</div>
            <div class="section-title">Experience</div>
            <div class="muted">{experience_html}</div>
            <div class="section-title">Education</div>
            <div class="muted">{education_html}</div>
            <div class="section-title">Resume Evidence</div>
            <div class="muted">{evidence}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summarize_events(events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not events:
        return {"avg_search": 0.0, "avg_extract": 0.0}
    query_times = [float(event.get("wall_seconds", 0)) for event in events if event.get("event_type") == "rag_query"]
    extract_times = [float(event.get("wall_seconds", 0)) for event in events if event.get("event_type") == "extract_resume"]
    return {
        "avg_search": round(sum(query_times) / len(query_times), 3) if query_times else 0.0,
        "avg_extract": round(sum(extract_times) / len(extract_times), 3) if extract_times else 0.0,
    }


service = ResumeRagService()

if "candidate_results" not in st.session_state:
    st.session_state["candidate_results"] = []
if "selected_candidate" not in st.session_state:
    st.session_state["selected_candidate"] = None

with st.sidebar:
    st.markdown("### Filters")
    domain_options = list(ALLOWED_DOMAINS)
    domain_display = {domain: domain_label(domain) for domain in domain_options}
    domains = st.multiselect(
        "Domains",
        domain_options,
        default=domain_options,
        format_func=lambda domain: domain_display[domain],
    )
    extraction_mode = st.selectbox("Extraction", list(EXTRACTION_MODES), format_func=mode_label)
    max_files = st.number_input("Files per domain", min_value=1, max_value=500, value=DEFAULT_MAX_FILES_PER_DOMAIN)
    top_k = st.slider("Results", min_value=1, max_value=10, value=5)
    dark_mode = st.toggle("Dark mode", value=False)

    st.divider()
    st.markdown("### Dataset Overview")
    profiles = service.list_profiles()
    events = service.monitor.read_events(limit=500)
    event_summary = summarize_events(events)
    st.metric("Resumes Indexed", len(profiles))
    st.metric("Retrieval", "TF-IDF")
    st.metric("Avg Search", f"{event_summary['avg_search']} sec")

    if st.button("Build / rebuild index", type="primary", width="stretch"):
        with st.spinner("Reading PDFs, extracting profiles, and rebuilding the search index..."):
            stats = service.ingest(
                domains=domains,
                max_files_per_domain=int(max_files),
                extraction_mode=extraction_mode,
            )
        st.success(f"Indexed {stats['processed']} resumes, {stats['chunks']} chunks.")

apply_theme(dark_mode)

st.markdown(
    """
    <div class="hero">
        <div>
            <h1 class="hero-title">Resume Intelligence Platform</h1>
            <div class="hero-subtitle">AI-powered candidate search across Banking and Information Technology resumes</div>
        </div>
        <div class="avatar">HR</div>
    </div>
    """,
    unsafe_allow_html=True,
)

profiles = service.list_profiles()
events = service.monitor.read_events(limit=500)
event_summary = summarize_events(events)
domain_counts = pd.Series([profile.get("domain", "Unknown") for profile in profiles]).value_counts() if profiles else pd.Series(dtype=int)

metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("Indexed CVs", str(len(profiles)), "Generated candidate profiles")
with metric_cols[1]:
    metric_card("Avg Search", f"{event_summary['avg_search']} sec", "Measured from local logs")
with metric_cols[2]:
    metric_card("Domains", str(len(domain_counts) or len(ALLOWED_DOMAINS)), "Banking and IT")
with metric_cols[3]:
    metric_card("Extraction", mode_label(extraction_mode), "Selected engine")

tab_search, tab_candidates, tab_analytics = st.tabs(["Search", "Candidates", "Analytics"])

with tab_search:
    search_col, detail_col = st.columns([2.1, 1], gap="large")
    with search_col:
        with st.form("candidate_search_form"):
            query = st.text_input(
                "Search candidates",
                placeholder="Find IT candidates with SQL, Python, and data analysis experience",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Search", type="primary", disabled=not query.strip(), width="stretch")

        if submitted:
            with st.spinner("Searching candidate evidence..."):
                response = service.ask(query, top_k=top_k)
            st.session_state["candidate_results"] = build_candidate_results(response["sources"])
            st.session_state["selected_candidate"] = (
                st.session_state["candidate_results"][0] if st.session_state["candidate_results"] else None
            )

        results = st.session_state["candidate_results"]
        st.markdown("### Results")
        if results:
            for index, profile in enumerate(results):
                render_candidate_card(profile, index)
        else:
            st.info("Search for candidates after building the index. Try: Find banking candidates with credit risk experience.")

    with detail_col:
        render_candidate_detail(st.session_state["selected_candidate"])

with tab_candidates:
    selected_domain = st.selectbox("Domain filter", ["All", *ALLOWED_DOMAINS], format_func=lambda item: "All" if item == "All" else domain_label(item))
    filtered_profiles = service.list_profiles(None if selected_domain == "All" else selected_domain)
    if filtered_profiles:
        table = pd.DataFrame(filtered_profiles)
        visible_cols = [
            col
            for col in ["candidate_name", "file_name", "domain", "email", "phone", "skills", "actual_extraction_engine"]
            if col in table.columns
        ]
        st.dataframe(table[visible_cols], width="stretch", height=520)
    else:
        st.info("No extracted profiles yet. Build the index from the sidebar first.")

with tab_analytics:
    phoenix_status = service.monitor.phoenix.status()
    analytics_cols = st.columns(3)
    with analytics_cols[0]:
        metric_card("Profiles", str(len(profiles)), "Extracted JSON records")
    with analytics_cols[1]:
        metric_card("Avg Extract", f"{event_summary['avg_extract']} sec", "Per resume")
    with analytics_cols[2]:
        phoenix_value = "Enabled" if phoenix_status["initialized"] else "Disabled"
        metric_card("Phoenix", phoenix_value, phoenix_status["ui"])

    st.markdown("### Candidates by Domain")
    if not domain_counts.empty:
        total = max(int(domain_counts.sum()), 1)
        for domain, count in domain_counts.items():
            width = round((int(count) / total) * 100)
            st.markdown(
                f"""
                <div class="candidate-meta">
                    <span>{domain_label(str(domain))}</span>
                    <span>{int(count)}</span>
                </div>
                <div class="domain-bar">
                    <div class="domain-fill" style="width:{width}%;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No profile distribution yet.")

    st.markdown("### Runtime Events")
    if events:
        df = pd.DataFrame(events)
        metric_fields = [
            col
            for col in [
                "event_type",
                "status",
                "started_at",
                "extraction_mode",
                "framework",
                "domain",
                "file_name",
                "wall_seconds",
                "cpu_seconds",
                "peak_memory_mb",
                "text_chars",
                "skills_count",
                "error",
            ]
            if col in df.columns
        ]
        st.dataframe(df[metric_fields], width="stretch", height=360)
    else:
        st.info("No monitoring events yet.")

