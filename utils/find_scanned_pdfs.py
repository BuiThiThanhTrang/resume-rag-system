import argparse
import sys
from pathlib import Path

import fitz

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import ALLOWED_DOMAINS, RAW_DATA_DIR
from utils.file_utils import iter_pdf_files


def text_chars_without_ocr(pdf_path: Path) -> int:
    with fitz.open(pdf_path) as doc:
        return sum(len(page.get_text("text").strip()) for page in doc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Print PDF paths that likely need OCR.")
    parser.add_argument("--domains", nargs="+", default=list(ALLOWED_DOMAINS), choices=list(ALLOWED_DOMAINS))
    parser.add_argument("--min-text-chars", type=int, default=80)
    args = parser.parse_args()

    scanned_count = 0
    total_count = 0

    for pdf_path in iter_pdf_files(RAW_DATA_DIR, args.domains):
        total_count += 1
        try:
            char_count = text_chars_without_ocr(pdf_path)
        except Exception as exc:
            print(f"ERROR\t{pdf_path}\t{exc}")
            continue

        if char_count < args.min_text_chars:
            scanned_count += 1
            print(pdf_path)

    print(f"\nScanned/needs OCR: {scanned_count}/{total_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
