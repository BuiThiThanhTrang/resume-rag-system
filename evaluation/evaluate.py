import argparse
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.env_loader import load_project_env

load_project_env(ROOT_DIR)

from services.rag_service import ResumeRagService


QUERIES = [
    "IT candidates with Python SQL and data analysis experience",
    "Banking candidates with loan credit risk or mortgage experience",
    "Candidates with customer service and finance background",
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run a lightweight RAG retrieval evaluation.")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    service = ResumeRagService()
    service.store.load()
    for query in QUERIES:
        start = time.perf_counter()
        response = service.ask(query, top_k=args.top_k)
        latency = time.perf_counter() - start
        print("=" * 80)
        print(f"Query: {query}")
        print(f"Latency: {latency:.3f}s")
        print(response["answer"])


if __name__ == "__main__":
    main()
