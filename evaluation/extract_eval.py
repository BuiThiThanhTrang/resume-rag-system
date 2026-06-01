import argparse
import csv
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import fitz

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import ALLOWED_DOMAINS, RAW_DATA_DIR
from services.pdf_service import PdfService
from services.resume_extractor import ExtractionMode, ResumeExtractor
from utils.file_utils import ensure_dir, iter_pdf_files, write_json


SCALAR_FIELDS = ("candidate_name", "email", "phone", "summary")
LIST_FIELDS = ("skills", "education", "experience")
ALL_FIELDS = ("file_name", "domain", *SCALAR_FIELDS, *LIST_FIELDS)


def normalize_scalar(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).lower().strip().split())


def normalize_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        value = [value]
    return sorted({normalize_scalar(item) for item in value if normalize_scalar(item)})


def list_f1(predicted: Iterable[str], expected: Iterable[str]) -> Tuple[float, float, float]:
    pred = set(predicted)
    gold = set(expected)
    if not pred and not gold:
        return 1.0, 1.0, 1.0
    if not pred or not gold:
        return 0.0, 0.0, 0.0
    true_positive = len(pred & gold)
    precision = true_positive / len(pred)
    recall = true_positive / len(gold)
    if precision + recall == 0:
        return precision, recall, 0.0
    return precision, recall, 2 * precision * recall / (precision + recall)


def load_ground_truth(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if not path or not path.exists():
        return {}
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return {item["file_name"]: item for item in payload}
        return payload
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return {row["file_name"]: row for row in csv.DictReader(handle)}
    raise ValueError("Ground truth must be a .json or .csv file")


def page_count(pdf_path: Path) -> int:
    with fitz.open(pdf_path) as doc:
        return doc.page_count


def score_with_ground_truth(prediction: Dict[str, Any], truth: Dict[str, Any]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    exact_scores = []
    for field in SCALAR_FIELDS:
        predicted = normalize_scalar(prediction.get(field))
        expected = normalize_scalar(truth.get(field))
        score = 1.0 if predicted == expected else 0.0
        scores[f"{field}_exact"] = score
        exact_scores.append(score)

    f1_scores = []
    for field in LIST_FIELDS:
        precision, recall, f1 = list_f1(normalize_list(prediction.get(field)), normalize_list(truth.get(field)))
        scores[f"{field}_precision"] = precision
        scores[f"{field}_recall"] = recall
        scores[f"{field}_f1"] = f1
        f1_scores.append(f1)

    scores["accuracy"] = sum(exact_scores + f1_scores) / max(len(exact_scores) + len(f1_scores), 1)
    return scores


def proxy_quality_score(prediction: Dict[str, Any], extracted_text: str) -> Dict[str, float]:
    checks = {
        "has_candidate_name": bool(prediction.get("candidate_name")),
        "has_email": bool(prediction.get("email")),
        "has_phone": bool(prediction.get("phone")),
        "has_skills": bool(prediction.get("skills")),
        "has_summary": len(str(prediction.get("summary", ""))) >= 80,
        "text_extracted": len(extracted_text) >= 500,
    }
    score = sum(1 for passed in checks.values() if passed) / len(checks)
    return {**{name: float(passed) for name, passed in checks.items()}, "proxy_accuracy": score}


def evaluate_file(
    pdf_path: Path,
    domain: str,
    pdf_service: PdfService,
    extractor: ResumeExtractor,
    ground_truth: Dict[str, Dict[str, Any]],
    extraction_mode: ExtractionMode,
) -> Dict[str, Any]:
    tracemalloc.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()

    text = pdf_service.extract_text(pdf_path)
    profile = extractor.extract(text, pdf_path.name, domain, mode=extraction_mode)

    cpu_seconds = time.process_time() - cpu_start
    wall_seconds = time.perf_counter() - wall_start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    row: Dict[str, Any] = {
        "file_name": pdf_path.name,
        "domain": domain,
        "pages": page_count(pdf_path),
        "chars": len(text),
        "wall_seconds": round(wall_seconds, 4),
        "cpu_seconds": round(cpu_seconds, 4),
        "peak_memory_mb": round(peak_bytes / (1024 * 1024), 3),
        "status": "ok",
        "extraction_mode": extraction_mode,
    }

    if pdf_path.name in ground_truth:
        row.update(score_with_ground_truth(profile, ground_truth[pdf_path.name]))
    else:
        row.update(proxy_quality_score(profile, text))

    row["profile"] = profile
    return row


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    if not ok_rows:
        return {"files": len(rows), "ok": 0}

    def avg(field: str) -> float:
        values = [float(row[field]) for row in ok_rows if field in row]
        return round(sum(values) / len(values), 4) if values else 0.0

    score_field = "accuracy" if "accuracy" in ok_rows[0] else "proxy_accuracy"
    return {
        "files": len(rows),
        "ok": len(ok_rows),
        "failed": len(rows) - len(ok_rows),
        "avg_wall_seconds": avg("wall_seconds"),
        "avg_cpu_seconds": avg("cpu_seconds"),
        "avg_peak_memory_mb": avg("peak_memory_mb"),
        f"avg_{score_field}": avg(score_field),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate PDF resume extraction speed, resources, and accuracy.")
    parser.add_argument("--domains", nargs="+", default=list(ALLOWED_DOMAINS), choices=list(ALLOWED_DOMAINS))
    parser.add_argument("--max-files-per-domain", type=int, default=10)
    parser.add_argument("--ground-truth", type=Path, default=None, help="Optional JSON/CSV labels keyed by file_name.")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "runtime_outputs" / "evaluation")
    parser.add_argument(
        "--extraction-mode",
        choices=["rule_based", "openai", "langchain_openai"],
        default="rule_based",
        help="Choose the extraction engine.",
    )
    args = parser.parse_args()

    ensure_dir(args.output_dir)
    ground_truth = load_ground_truth(args.ground_truth)
    pdf_service = PdfService()
    extractor = ResumeExtractor()
    rows: List[Dict[str, Any]] = []

    selected_files: List[Path] = []
    for domain in args.domains:
        selected_files.extend(iter_pdf_files(RAW_DATA_DIR, [domain])[: args.max_files_per_domain])

    for pdf_path in selected_files:
        try:
            row = evaluate_file(
                pdf_path=pdf_path,
                domain=pdf_path.parent.name,
                pdf_service=pdf_service,
                extractor=extractor,
                ground_truth=ground_truth,
                extraction_mode=args.extraction_mode,
            )
        except Exception as exc:
            row = {
                "file_name": pdf_path.name,
                "domain": pdf_path.parent.name,
                "status": "failed",
                "error": str(exc),
            }
        rows.append(row)
        print(f"{row['status']:>6} {row['domain']:<24} {row['file_name']:<16} {row.get('wall_seconds', '-')}s")

    report = {"summary": summarize(rows), "rows": rows}
    write_json(args.output_dir / "extract_eval_report.json", report)

    csv_path = args.output_dir / "extract_eval_metrics.csv"
    metric_fields = sorted({key for row in rows for key in row.keys() if key != "profile"})
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=metric_fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in metric_fields} for row in rows)

    print("\nSummary")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"\nWrote: {args.output_dir / 'extract_eval_report.json'}")
    print(f"Wrote: {csv_path}")


if __name__ == "__main__":
    main()
