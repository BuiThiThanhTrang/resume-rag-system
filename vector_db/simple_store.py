import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from utils.file_utils import ensure_dir
from utils.text_utils import build_idf, cosine_similarity, tfidf_vector, tokenize


@dataclass
class SearchResult:
    score: float
    text: str
    metadata: Dict[str, str]


class SimpleVectorStore:
    def __init__(self, store_dir: Path):
        self.store_dir = store_dir
        self.index_path = store_dir / "tfidf_index.pkl"
        self.documents: List[Dict[str, object]] = []
        self.idf: Dict[str, float] = {}

    def build(self, chunks: List[Dict[str, object]]) -> None:
        tokenized = [tokenize(str(chunk["text"])) for chunk in chunks]
        self.idf = build_idf(tokenized)
        self.documents = []
        for chunk, tokens in zip(chunks, tokenized):
            self.documents.append(
                {
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "vector": tfidf_vector(tokens, self.idf),
                }
            )
        ensure_dir(self.store_dir)
        with self.index_path.open("wb") as handle:
            pickle.dump({"idf": self.idf, "documents": self.documents}, handle)

    def load(self) -> bool:
        if not self.index_path.exists():
            return False
        with self.index_path.open("rb") as handle:
            payload = pickle.load(handle)
        self.idf = payload["idf"]
        self.documents = payload["documents"]
        return True

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        query_vector = tfidf_vector(tokenize(query), self.idf)
        scored = []
        for doc in self.documents:
            score = cosine_similarity(query_vector, doc["vector"])
            if score > 0:
                scored.append(SearchResult(score=score, text=str(doc["text"]), metadata=dict(doc["metadata"])))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

