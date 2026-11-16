"""Steps 2-4: load, clean, chunk, embed and upsert the SENTINEL corpus into Qdrant.

    python scripts/ingest.py                 # create collection if missing, upsert all chunks
    python scripts/ingest.py --recreate      # drop and rebuild the collection
    python scripts/ingest.py --raw-dir path/to/your/corpus

Writes for inspection:
    data/processed/documents.jsonl   cleaned documents
    data/processed/chunks.jsonl      chunks exactly as embedded
    results/ingest_summary.json      counts and settings
"""

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rich.console import Console  # noqa: E402
from rich.progress import Progress  # noqa: E402
from rich.table import Table  # noqa: E402

from sentinel_rag.chunking import chunk_documents  # noqa: E402
from sentinel_rag.cleaning import load_corpus  # noqa: E402
from sentinel_rag.config import get_settings  # noqa: E402
from sentinel_rag.embeddings import EmbeddingCache, embed_texts, format_document, get_embedder  # noqa: E402
from sentinel_rag.store import ensure_collection, get_client, upsert_chunks  # noqa: E402

console = Console()


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, default=None)
    ap.add_argument("--recreate", action="store_true", help="drop and recreate the collection")
    args = ap.parse_args()
    s = get_settings()
    raw_dir = args.raw_dir or s.raw_dir
    t_start = time.perf_counter()

    # 2. load + clean + chunk -------------------------------------------------
    console.rule("[bold]1/4 Load and clean")
    docs, dupes = load_corpus(raw_dir)
    if len(docs) < 200:
        console.print(f"[yellow]Only {len(docs)} documents found; the assignment asks for at least 200.[/]")
    by_type = Counter(d.doc_type for d in docs)
    console.print(f"{len(docs)} unique documents ({dupes} duplicates dropped): {dict(by_type)}")
    write_jsonl(s.processed_dir / "documents.jsonl", (d.to_dict() for d in docs))

    console.rule(f"[bold]2/4 Chunk (size={s.chunk_size} chars, overlap={s.chunk_overlap} chars)")
    chunks = chunk_documents(docs, s.chunk_size, s.chunk_overlap)
    lengths = sorted(len(c.text) for c in chunks)
    console.print(f"{len(chunks)} chunks | median {lengths[len(lengths) // 2]} chars | min {lengths[0]} | max {lengths[-1]}")
    write_jsonl(s.processed_dir / "chunks.jsonl", (c.to_dict() for c in chunks))

    # 3. embed ----------------------------------------------------------------
    console.rule(f"[bold]3/4 Embed with {s.embed_model} ({s.embed_dim} dims, provider={s.provider})")
    embedder = get_embedder(s)
    cache = EmbeddingCache(s.cache_dir, embedder.model, embedder.dim)
    texts = [format_document(c.title, c.text) for c in chunks]
    cached = sum(1 for t in texts if cache.get(t) is not None)
    console.print(f"{cached} chunks already in cache, {len(texts) - cached} to embed")
    with Progress(console=console) as bar:
        task = bar.add_task("embedding", total=len(texts) - cached)
        vectors = embed_texts(embedder, texts, cache, s.embed_batch_size, s.embed_pause_s,
                              progress=lambda n: bar.advance(task, n))

    # 4. upsert ---------------------------------------------------------------
    console.rule(f"[bold]4/4 Upsert into Qdrant collection '{s.collection}'")
    client = get_client(s)
    ensure_collection(client, s.collection, embedder.dim, recreate=args.recreate)
    with Progress(console=console) as bar:
        task = bar.add_task("upserting", total=len(chunks))
        upsert_chunks(client, s.collection, chunks, vectors, progress=lambda n: bar.advance(task, n))

    info = client.get_collection(s.collection)
    count = client.count(s.collection, exact=True).count
    table = Table(title="Collection")
    for col in ("name", "points", "vector size", "distance", "status"):
        table.add_column(col)
    table.add_row(s.collection, str(count), str(info.config.params.vectors.size),
                  str(info.config.params.vectors.distance.value), str(info.status.value))
    console.print(table)

    summary = {
        "documents": len(docs), "duplicates_dropped": dupes, "documents_by_type": dict(by_type),
        "chunks": len(chunks), "chunk_size_chars": s.chunk_size, "chunk_overlap_chars": s.chunk_overlap,
        "chunk_length_median": lengths[len(lengths) // 2], "embedding_provider": s.provider,
        "embedding_model": embedder.model, "vector_size": embedder.dim, "distance": "Cosine",
        "collection": s.collection, "points_in_collection": count,
        "seconds": round(time.perf_counter() - t_start, 1),
    }
    s.results_dir.mkdir(parents=True, exist_ok=True)
    (s.results_dir / "ingest_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    console.print(f"[green]Done[/] in {summary['seconds']} s. Summary written to results/ingest_summary.json")


if __name__ == "__main__":
    main()
