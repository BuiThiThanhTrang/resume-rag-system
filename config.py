from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "store"
RUNTIME_OUTPUT_DIR = BASE_DIR / "runtime_outputs"


def _writable_dir(preferred: Path) -> Path:
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / f".write_probe_{uuid4().hex}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return preferred
    except OSError:
        fallback = RUNTIME_OUTPUT_DIR / preferred.name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


EXTRACTED_JSON_DIR = _writable_dir(BASE_DIR / "extracted_json")

ALLOWED_DOMAINS = ("BANKING", "INFORMATION-TECHNOLOGY")
DEFAULT_MAX_FILES_PER_DOMAIN = 50
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
