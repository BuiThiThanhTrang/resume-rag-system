import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


EMAIL_RE = re.compile(r"[\w.\-+]+@[\w.\-]+\.\w+")
PHONE_RE = re.compile(r"(?:(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4})")
SKILLS = {
    "python", "java", "sql", "excel", "power bi", "tableau", "aws", "azure",
    "docker", "kubernetes", "linux", "git", "react", "node", "javascript",
    "machine learning", "deep learning", "tensorflow", "pytorch", "nlp",
    "risk", "credit", "loan", "mortgage", "banking", "finance", "audit",
    "customer service", "salesforce", "etl", "data analysis",
}


class ResumeProfile(BaseModel):
    file_name: str
    domain: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    summary: str = ""


class ResumeExtractor:
    def extract(self, text: str, file_name: str, domain: str, use_llm: bool = False) -> Dict[str, Any]:
        if use_llm and os.getenv("OPENAI_API_KEY"):
            llm_result = self._extract_with_openai(text, file_name, domain)
            if llm_result:
                return llm_result
        return self._extract_with_rules(text, file_name, domain).model_dump()

    def _extract_with_rules(self, text: str, file_name: str, domain: str) -> ResumeProfile:
        lines = [line.strip() for line in re.split(r"[\n\r]+| {2,}", text) if line.strip()]
        email = EMAIL_RE.search(text)
        phone = PHONE_RE.search(text)
        lower_text = text.lower()
        skills = sorted(skill for skill in SKILLS if skill in lower_text)
        education = self._section_lines(lines, ("education", "academic"), limit=6)
        experience = self._section_lines(lines, ("experience", "employment", "work history"), limit=8)
        name = self._guess_name(lines, email.group(0) if email else None)
        summary = " ".join(lines[:6])[:900]
        return ResumeProfile(
            file_name=file_name,
            domain=domain,
            candidate_name=name,
            email=email.group(0) if email else None,
            phone=phone.group(0) if phone else None,
            skills=skills[:30],
            education=education,
            experience=experience,
            summary=summary,
        )

    def _guess_name(self, lines: List[str], email: Optional[str]) -> Optional[str]:
        for line in lines[:8]:
            if EMAIL_RE.search(line) or PHONE_RE.search(line):
                continue
            words = line.split()
            if 2 <= len(words) <= 5 and all(word[:1].isalpha() for word in words):
                if not any(marker in line.lower() for marker in ("resume", "curriculum", "email", "phone")):
                    return line.title()
        if email:
            return email.split("@", 1)[0].replace(".", " ").replace("_", " ").title()
        return None

    def _section_lines(self, lines: List[str], headers: tuple[str, ...], limit: int) -> List[str]:
        selected: List[str] = []
        capture = False
        for line in lines:
            lower = line.lower()
            if any(header in lower for header in headers):
                capture = True
                continue
            if capture and any(stop in lower for stop in ("skills", "education", "experience", "certification", "summary")):
                if not any(header in lower for header in headers):
                    break
            if capture and 20 <= len(line) <= 220:
                selected.append(line)
            if len(selected) >= limit:
                break
        return selected

    def _extract_with_openai(self, text: str, file_name: str, domain: str) -> Optional[Dict[str, Any]]:
        try:
            from openai import OpenAI

            client = OpenAI()
            prompt = Path("prompts/extraction_prompt.txt").read_text(encoding="utf-8")
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"File: {file_name}\nDomain: {domain}\nResume text:\n{text[:12000]}"},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            payload = json.loads(response.choices[0].message.content or "{}")
            payload.setdefault("file_name", file_name)
            payload.setdefault("domain", domain)
            return payload
        except Exception:
            return None

