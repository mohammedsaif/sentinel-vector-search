"""Offline tests: no API keys or network needed (in-memory Qdrant + fake embedder)."""

import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sentinel_rag.chunking import chunk_documents, split_text  # noqa: E402
from sentinel_rag.cleaning import clean_text, load_corpus  # noqa: E402
from sentinel_rag.config import get_settings  # noqa: E402
from sentinel_rag.embeddings import FakeEmbedder, embed_texts, format_document, format_query  # noqa: E402
from sentinel_rag.store import ensure_collection, get_client, search, upsert_chunks  # noqa: E402

RAW = ROOT / "data" / "raw"


def test_clean_removes_boilerplate():
    raw = "SENTINEL KNOWLEDGE BASE  |  CONFIDENTIAL\r\n\r\nReal  text’s here.   \r\nPage 1 of 2\r\n\fMore."
    out = clean_text(raw)
    assert "SENTINEL" not in out and "Page 1" not in out
    assert "Real text's here." in out and "\r" not in out and "\f" not in out


def test_corpus_has_200_unique_docs():
    docs, dupes = load_corpus(RAW)
    assert len(docs) >= 200
    assert dupes == 6
    assert {d.doc_type for d in docs} == {"guideline", "playbook", "investigator_note", "chargeback"}


def test_chunks_respect_size_and_overlap():
    text = " ".join(f"Sentence number {i} talks about fraud checks." for i in range(80))
    chunks = split_text(text, chunk_size=300, chunk_overlap=60)
    assert all(len(c) <= 300 for c in chunks)
    for a, b in zip(chunks, chunks[1:]):  # next chunk starts with the tail of the previous one
        assert a.endswith(b.split(". ")[0] + ".")


def test_headings_stay_with_their_text():
    docs, _ = load_corpus(RAW)
    for c in chunk_documents(docs, 900, 150):
        assert not c.text.rstrip().endswith(("Outcome", "Observations", "Customer negligence"))


def test_end_to_end_in_memory():
    s = replace(get_settings(), qdrant_url=":memory:", provider="fake", collection="test")
    docs, _ = load_corpus(RAW)
    chunks = chunk_documents(docs, s.chunk_size, s.chunk_overlap)
    emb = FakeEmbedder(s)
    vectors = embed_texts(emb, [format_document(c.title, c.text) for c in chunks], cache=None)
    client = get_client(s)
    ensure_collection(client, s.collection, emb.dim)
    upsert_chunks(client, s.collection, chunks, vectors)
    upsert_chunks(client, s.collection, chunks, vectors)  # idempotent: same IDs, no duplicates
    assert client.count(s.collection).count == len(chunks)

    qv = emb.embed_batch([format_query("new device large payment to new beneficiary")])[0]
    hits = search(client, s.collection, qv, limit=5)
    assert len(hits) == 5 and hits[0].score >= hits[-1].score
    assert {"source_document", "doc_type", "chunk_number"} <= set(hits[0].payload)

    filtered = search(client, s.collection, qv, limit=5, doc_type="chargeback")
    assert filtered and all(h.payload["doc_type"] == "chargeback" for h in filtered)
