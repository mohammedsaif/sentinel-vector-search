"""Sentence-aware chunking with character-based size and overlap.

Why characters and not tokens: it needs no tokenizer download, is easy to
explain, and for English text 1 token is about 4-4.5 characters, so 900
characters is about 200-225 tokens.

How it works
1. Split the document into paragraphs, then into sentences.
2. Pack whole sentences into a chunk until adding the next one would pass
   `chunk_size` characters.
3. Start the next chunk with the last few sentences of the previous chunk,
   up to `chunk_overlap` characters, so a rule and its condition are not
   separated at a boundary.
4. Section headings are glued to the sentence after them.
5. A single sentence longer than `chunk_size` is split on word boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from .cleaning import Document

_SENTENCE_END = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z0-9\"'(])")
_LIST_NUMBER = re.compile(r"^\d{1,3}[.)]$")


@dataclass
class Chunk:
    chunk_id: str
    source_document: str
    doc_type: str
    title: str
    chunk_number: int  # 1-based position inside the document
    total_chunks: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def _units(text: str, chunk_size: int) -> list[str]:
    """Sentences (and list items / headings) in reading order."""
    units: list[str] = []
    heading = ""
    for para in text.split("\n\n"):
        for line in para.split("\n"):  # list items and headings sit on their own lines
            line = line.strip()
            if not line:
                continue
            if _is_heading(line):
                # keep a heading attached to the sentence that follows it
                heading = f"{heading} {line}".strip() if heading else line
                continue
            if heading:
                line, heading = f"{heading}: {line}", ""
            for sent in _sentences(line):
                if len(sent) <= chunk_size:
                    units.append(sent)
                    continue
                words, buf = sent.split(), ""
                for w in words:  # very long sentence: hard split on words
                    if len(buf) + len(w) + 1 > chunk_size and buf:
                        units.append(buf)
                        buf = w
                    else:
                        buf = f"{buf} {w}".strip()
                if buf:
                    units.append(buf)
    if heading:
        units.append(heading)
    return units


def _sentences(line: str) -> list[str]:
    """Split a line into sentences, keeping list numbers like '3.' with the text after them."""
    out: list[str] = []
    prefix = ""
    for part in _SENTENCE_END.split(line):
        part = part.strip()
        if _LIST_NUMBER.match(part):
            prefix = f"{prefix}{part} "
            continue
        out.append(prefix + part)
        prefix = ""
    if prefix:
        out.append(prefix.strip())
    return out


def _is_heading(line: str) -> bool:
    """Short line with no sentence punctuation, e.g. '4. Customer negligence' or 'Outcome'."""
    return len(line) <= 60 and not line.endswith((".", "!", "?", ":", ";", '"')) and not line.startswith("-")


def split_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list[str]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    units = _units(text, chunk_size)
    chunks: list[str] = []
    current: list[str] = []
    length = 0

    for unit in units:
        added = len(unit) + (1 if current else 0)
        if current and length + added > chunk_size:
            chunks.append(" ".join(current))
            # carry trailing sentences forward as overlap
            carry: list[str] = []
            carry_len = 0
            for prev in reversed(current):
                if carry_len + len(prev) + 1 > chunk_overlap:
                    break
                carry.insert(0, prev)
                carry_len += len(prev) + 1
            current, length = carry, max(carry_len - 1, 0)
            added = len(unit) + (1 if current else 0)
        current.append(unit)
        length += added

    if current:
        tail = " ".join(current)
        # don't emit a final chunk that is only overlap already present in the previous chunk
        if not chunks or not chunks[-1].endswith(tail):
            chunks.append(tail)
    return chunks


def chunk_documents(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    out: list[Chunk] = []
    for doc in docs:
        pieces = split_text(doc.text, chunk_size, chunk_overlap)
        for i, piece in enumerate(pieces, 1):
            out.append(Chunk(chunk_id=f"{doc.source_document}#{i}", source_document=doc.source_document,
                             doc_type=doc.doc_type, title=doc.title, chunk_number=i,
                             total_chunks=len(pieces), text=piece))
    return out
