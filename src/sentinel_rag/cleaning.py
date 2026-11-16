"""Load raw documents from disk and clean them.

Folder convention: data/raw/<doc_type>/<file>.txt|.md
The sub-folder name becomes the `doc_type` payload field, so your pod's real
corpus can be dropped in using the same layout.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

# Lines that are export clutter, not content.
BOILERPLATE = [
    re.compile(r"^\s*SENTINEL KNOWLEDGE BASE\b.*$", re.I),
    re.compile(r"^\s*CONFIDENTIAL\b.*$", re.I),
    re.compile(r"^\s*Page\s+\d+\s+(of|/)\s+\d+\s*$", re.I),
    re.compile(r"^\s*-\s*\d+\s*-\s*$"),  # "- 3 -" style page numbers
    re.compile(r"^\s*Note: synthetic summary prepared for the SENTINEL.*$", re.I),  # repeated disclaimer
]

QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", " ": " "}


@dataclass
class Document:
    doc_id: str
    source_document: str  # file path relative to the raw folder
    doc_type: str
    title: str
    text: str
    sha256: str

    def to_dict(self) -> dict:
        return asdict(self)


def clean_text(raw: str) -> str:
    """Normalise unicode and whitespace, drop headers/footers, keep paragraphs."""
    text = unicodedata.normalize("NFKC", raw)
    for bad, good in QUOTES.items():
        text = text.replace(bad, good)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")

    lines = []
    for line in text.split("\n"):
        if any(p.match(line) for p in BOILERPLATE):
            continue
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)  # at most one blank line between paragraphs
    return text.strip()


def _title_from(text: str, path: Path) -> tuple[str, str]:
    """Use the first line as the title when it is a short heading; drop it from the body."""
    first, _, rest = text.partition("\n")
    if first and len(first) <= 150 and (first.isupper() or not first.endswith(".")):
        title = first if not first.isupper() else first.title().replace("Rbi", "RBI").replace("Npci", "NPCI").replace("Mha", "MHA").replace("Sen-", "SEN-")
        return title, rest.strip()
    return path.stem.replace("-", " ").replace("_", " ").title(), text


def load_corpus(raw_dir: Path) -> tuple[list[Document], int]:
    """Return (unique cleaned documents, number of duplicates dropped)."""
    docs: list[Document] = []
    seen: set[str] = set()
    duplicates = 0
    for path in sorted(raw_dir.rglob("*")):
        if path.suffix.lower() not in {".txt", ".md"} or not path.is_file():
            continue
        cleaned = clean_text(path.read_text(encoding="utf-8", errors="replace"))
        if len(cleaned) < 50:  # empty or near-empty export
            continue
        digest = hashlib.sha256(cleaned.encode()).hexdigest()
        if digest in seen:
            duplicates += 1
            continue
        seen.add(digest)
        rel = path.relative_to(raw_dir)
        doc_type = rel.parts[0] if len(rel.parts) > 1 else "unknown"
        title, body = _title_from(cleaned, path)
        docs.append(Document(doc_id=path.stem, source_document=str(rel).replace("\\", "/"),
                             doc_type=doc_type, title=title, text=body, sha256=digest))
    return docs, duplicates
