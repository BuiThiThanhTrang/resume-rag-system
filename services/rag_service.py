from pathlib import Path
from typing import Dict, Iterable, List

from config import CHUNK_OVERLAP, CHUNK_SIZE, EXTRACTED_JSON_DIR, RAW_DATA_DIR, VECTOR_DB_DIR
from services.pdf_service import PdfService
from services.resume_extractor import ResumeExtractor
from utils.file_utils import iter_pdf_files, read_json, write_json
from utils.text_utils import chunk_text
from vector_db.simple_store import SearchResult, SimpleVectorStore


class ResumeRagService:
    def __init__(self):
        self.pdf_service = PdfService()
        self.extractor = ResumeExtractor()
        self.store = SimpleVectorStore(VECTOR_DB_DIR)

    def ingest(self, domains: Iterable[str], max_files_per_domain: int = 50, use_llm: bool = False) -> Dict[str, int]:
        chunks: List[Dict[str, object]] = []
        processed = 0
        failed = 0
        for pdf_path in self._limited_files(domains, max_files_per_domain):
            domain = pdf_path.parent.name
            try:
                text = self.pdf_service.extract_text(pdf_path)
                profile = self.extractor.extract(text, pdf_path.name, domain, use_llm=use_llm)
                json_path = EXTRACTED_JSON_DIR / domain / f"{pdf_path.stem}.json"
                write_json(json_path, profile)
                for chunk_index, chunk in enumerate(chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)):
                    chunks.append(
                        {
                            "text": chunk,
                            "metadata": {
                                "file_name": pdf_path.name,
                                "domain": domain,
                                "chunk": str(chunk_index),
                                "json_path": str(json_path),
                            },
                        }
                    )
                processed += 1
            except Exception:
                failed += 1
        self.store.build(chunks)
        return {"processed": processed, "failed": failed, "chunks": len(chunks)}

    def ask(self, query: str, top_k: int = 5) -> Dict[str, object]:
        if not self.store.documents:
            self.store.load()
        results = self.store.search(query, top_k=top_k)
        return {
            "answer": self._compose_answer(query, results),
            "sources": [result.__dict__ for result in results],
        }

    def list_profiles(self, domain: str | None = None) -> List[Dict[str, object]]:
        root = EXTRACTED_JSON_DIR if domain is None else EXTRACTED_JSON_DIR / domain
        if not root.exists():
            return []
        return [read_json(path) for path in sorted(root.rglob("*.json"))]

    def _limited_files(self, domains: Iterable[str], max_files_per_domain: int) -> List[Path]:
        selected: List[Path] = []
        for domain in domains:
            selected.extend(iter_pdf_files(RAW_DATA_DIR, [domain])[:max_files_per_domain])
        return selected

    def _compose_answer(self, query: str, results: List[SearchResult]) -> str:
        if not results:
            return "No matching resume context was found. Build the index first or broaden the query."
        lines = [f"Query: {query}", "", "Most relevant resume evidence:"]
        for index, result in enumerate(results, start=1):
            meta = result.metadata
            snippet = result.text[:550].replace("\n", " ")
            lines.append(f"{index}. {meta.get('file_name')} ({meta.get('domain')}) - score {result.score:.3f}: {snippet}")
        return "\n".join(lines)

