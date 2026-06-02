import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import ALLOWED_DOMAINS, DEFAULT_MAX_FILES_PER_DOMAIN, EXTRACTION_MODES
from services.rag_service import ResumeRagService
from utils.env_loader import load_project_env
from utils.file_utils import read_json

load_project_env(ROOT_DIR)

app = FastAPI(title="Resume RAG API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ResumeRagService()


class IngestRequest(BaseModel):
    domains: List[str] = Field(default_factory=lambda: list(ALLOWED_DOMAINS))
    max_files_per_domain: int = DEFAULT_MAX_FILES_PER_DOMAIN
    extraction_mode: str = "rule_based"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/config")
def get_config() -> dict:
    return {
        "domains": list(ALLOWED_DOMAINS),
        "extraction_modes": list(EXTRACTION_MODES),
        "default_max_files_per_domain": DEFAULT_MAX_FILES_PER_DOMAIN,
        "phoenix": service.monitor.phoenix.status(),
    }


@app.post("/api/ingest")
def ingest(request: IngestRequest) -> dict:
    stats = service.ingest(
        domains=request.domains,
        max_files_per_domain=request.max_files_per_domain,
        extraction_mode=request.extraction_mode,
    )
    return stats


@app.post("/api/search")
def search(request: SearchRequest) -> dict:
    response = service.ask(request.query, top_k=request.top_k)
    for source in response.get("sources", []):
        metadata = source.get("metadata", {})
        json_path = metadata.get("json_path")
        if json_path and Path(json_path).exists():
            try:
                source["profile"] = read_json(Path(json_path))
            except Exception:
                source["profile"] = {}
        else:
            source["profile"] = {}
    return response


@app.get("/api/profiles")
def profiles(domain: Optional[str] = None) -> dict:
    selected_domain = None if domain in (None, "", "All") else domain
    return {"profiles": service.list_profiles(selected_domain)}


@app.get("/api/events")
def events(limit: int = 500) -> dict:
    return {"events": service.monitor.read_events(limit=limit)}


@app.delete("/api/events")
def clear_events() -> dict:
    service.monitor.clear()
    return {"status": "cleared"}


@app.get("/api/analytics")
def analytics() -> dict:
    profiles_data = service.list_profiles()
    events_data = service.monitor.read_events(limit=500)
    domain_counts: dict[str, int] = {}
    for profile in profiles_data:
        domain = str(profile.get("domain", "Unknown"))
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    query_times = [float(event.get("wall_seconds", 0)) for event in events_data if event.get("event_type") == "rag_query"]
    extract_times = [float(event.get("wall_seconds", 0)) for event in events_data if event.get("event_type") == "extract_resume"]
    return {
        "profiles_count": len(profiles_data),
        "domain_counts": domain_counts,
        "avg_search_seconds": round(sum(query_times) / len(query_times), 3) if query_times else 0,
        "avg_extract_seconds": round(sum(extract_times) / len(extract_times), 3) if extract_times else 0,
        "phoenix": service.monitor.phoenix.status(),
    }
