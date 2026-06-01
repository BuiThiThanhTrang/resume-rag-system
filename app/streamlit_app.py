import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import ALLOWED_DOMAINS, DEFAULT_MAX_FILES_PER_DOMAIN, EXTRACTION_MODES
from services.rag_service import ResumeRagService


st.set_page_config(page_title="Resume RAG System", layout="wide")
st.title("Resume RAG System")

service = ResumeRagService()

with st.sidebar:
    st.header("Index resumes")
    domains = st.multiselect("Domains", list(ALLOWED_DOMAINS), default=list(ALLOWED_DOMAINS))
    max_files = st.number_input("Max files per domain", min_value=1, max_value=500, value=DEFAULT_MAX_FILES_PER_DOMAIN)
    extraction_mode = st.selectbox(
        "Extraction mode",
        list(EXTRACTION_MODES),
        format_func=lambda item: {
            "rule_based": "Rule-based (offline)",
            "openai": "OpenAI SDK",
            "langchain_openai": "LangChain + OpenAI",
        }[item],
    )
    if st.button("Build / rebuild index", type="primary"):
        with st.spinner("Reading PDFs, extracting JSON, and building search index..."):
            stats = service.ingest(
                domains=domains,
                max_files_per_domain=int(max_files),
                extraction_mode=extraction_mode,
            )
        st.success(f"Processed {stats['processed']} files, failed {stats['failed']}, indexed {stats['chunks']} chunks.")

tab_chat, tab_profiles, tab_monitoring = st.tabs(["HR Query", "Extracted Profiles", "Monitoring"])

with tab_chat:
    query = st.text_area(
        "Ask about candidates",
        placeholder="Example: Find IT candidates with Python and SQL experience, or banking candidates with credit risk experience.",
        height=110,
    )
    top_k = st.slider("Number of evidence chunks", min_value=1, max_value=10, value=5)
    if st.button("Search", disabled=not query.strip()):
        response = service.ask(query, top_k=top_k)
        st.subheader("Answer")
        st.text(response["answer"])
        st.subheader("Sources")
        for source in response["sources"]:
            st.write(
                {
                    "score": round(source["score"], 3),
                    "file_name": source["metadata"].get("file_name"),
                    "domain": source["metadata"].get("domain"),
                    "chunk": source["metadata"].get("chunk"),
                }
            )

with tab_profiles:
    selected_domain = st.selectbox("Domain filter", ["All", *ALLOWED_DOMAINS])
    profiles = service.list_profiles(None if selected_domain == "All" else selected_domain)
    if profiles:
        st.dataframe(pd.DataFrame(profiles), use_container_width=True)
    else:
        st.info("No extracted JSON profiles yet. Build the index from the sidebar first.")

with tab_monitoring:
    col_left, col_right = st.columns([1, 4])
    with col_left:
        if st.button("Clear logs"):
            service.monitor.clear()
            st.rerun()
    phoenix_status = service.monitor.phoenix.status()
    st.subheader("Phoenix")
    if phoenix_status["initialized"]:
        st.success(f"Phoenix tracing enabled: {phoenix_status['ui']}")
    elif phoenix_status["available"]:
        st.warning(f"Phoenix packages are installed but tracing did not initialize: {phoenix_status['error']}")
    else:
        st.info("Phoenix tracing is not installed yet. Install the Phoenix packages and run `phoenix serve`.")
    st.caption(f"Project: {phoenix_status['project_name']} | Collector: {phoenix_status['endpoint']}")

    events = service.monitor.read_events(limit=500)
    if events:
        df = pd.DataFrame(events)
        metric_cols = [col for col in ["event_type", "status", "started_at", "extraction_mode", "framework", "domain", "file_name", "wall_seconds", "cpu_seconds", "peak_memory_mb", "text_chars", "skills_count", "error"] if col in df.columns]
        st.dataframe(df[metric_cols], use_container_width=True)
        numeric_cols = [col for col in ["wall_seconds", "cpu_seconds", "peak_memory_mb", "text_chars"] if col in df.columns]
        if numeric_cols:
            st.subheader("Average Metrics")
            st.dataframe(df.groupby("event_type")[numeric_cols].mean().round(4), use_container_width=True)
    else:
        st.info("No monitoring events yet. Build the index or run a query first.")
