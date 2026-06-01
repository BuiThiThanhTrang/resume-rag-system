import re
import unicodedata
from collections import Counter
from math import log, sqrt
from typing import Dict, Iterable, List


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = "".join(
        char for char in text
        if char in "\n\t" or not unicodedata.category(char).startswith("C")
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def build_idf(tokenized_docs: Iterable[List[str]]) -> Dict[str, float]:
    docs = list(tokenized_docs)
    doc_count = max(len(docs), 1)
    df = Counter()
    for tokens in docs:
        df.update(set(tokens))
    return {term: log((1 + doc_count) / (1 + freq)) + 1 for term, freq in df.items()}


def tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    counts = Counter(tokens)
    total = max(sum(counts.values()), 1)
    return {term: (count / total) * idf.get(term, 0.0) for term, count in counts.items()}


def cosine_similarity(left: Dict[str, float], right: Dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(term, 0.0) for term, value in left.items())
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
