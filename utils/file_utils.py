import json
from pathlib import Path
from typing import Any, Iterable, List


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_pdf_files(root: Path, domains: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for domain in domains:
        domain_dir = root / domain
        if domain_dir.exists():
            files.extend(sorted(domain_dir.glob("*.pdf")))
    return files

