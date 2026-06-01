from pathlib import Path
from typing import Optional

import fitz

from utils.text_utils import clean_text


class PdfService:
    def extract_text(self, pdf_path: Path, use_ocr: bool = True) -> str:
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            text = page.get_text("text")
            if len(text.strip()) < 30 and use_ocr:
                text = self._ocr_page(page)
            pages.append(text)
        return clean_text("\n".join(pages))

    def _ocr_page(self, page: fitz.Page) -> str:
        try:
            import pytesseract
            from PIL import Image

            pix = page.get_pixmap(dpi=200)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return pytesseract.image_to_string(image)
        except Exception:
            return ""


def extract_text_from_pdf(pdf_path: str | Path, use_ocr: bool = True) -> str:
    return PdfService().extract_text(Path(pdf_path), use_ocr=use_ocr)
