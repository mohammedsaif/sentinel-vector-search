"""Step 5: run 10 natural-language searches plus one filtered search, top 5 results with scores.

    python scripts/search.py                              # the 11 assignment queries
    python scripts/search.py -q "your question"           # ad-hoc query
    python scripts/search.py -q "your question" --doc-type playbook

Results are also written to results/search_results.md and results/search_results.json.
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402

from sentinel_rag.config import get_settings  # noqa: E402
from sentinel_rag.embeddings import EmbeddingCache, embed_texts, format_query, get_embedder  # noqa: E402
from sentinel_rag.store import get_client, search  # noqa: E402

QUERIES = [
    "What should an investigator check when a new device makes a large payment?",
    "A customer reported an unauthorised debit five days after the alert. How much of the loss do they bear?",
    "How do we spot an account that receives money from many victims and moves it out quickly?",
    "The victim was selling a sofa online and the buyer sent a QR code saying scan it to receive the money",
    "How many days does the bank have to credit the disputed amount back to the customer?",
    "The customer's phone suddenly lost signal in the evening and then money was transferred out",
    "Merchant ticket sizes do not match its business category and customers don't recognise the merchant name",
    "Elderly customer kept on a video call by people claiming to be police broke an FD and transferred money",
    "My UPI payment failed but the money was debited from my account. When will I get it back?",
    "What evidence does a merchant need to win a goods-not-received dispute?",
]
FILTERED = ("Customer shared an OTP with a caller pretending to be from the bank", "investigator_note")

console = Console()


def show(client, s, vector, query: str, doc_type: str | None, k: int) -> dict:
    hits = search(client, s.collection, vector, limit=k, doc_type=doc_type)
    title = f"[bold]{query}[/]" + (f"\n[cyan]filter: doc_type = {doc_type}[/]" if doc_type else "")
    table = Table(title=title, title_justify="left", show_lines=True, expand=True)
    table.add_column("#", width=2)
    table.add_column("score", width=6)
    table.add_column("doc_type", width=17)
    table.add_column("source_document / chunk", width=34, overflow="fold")
    table.add_column("text", ratio=1)
    rows = []
    for rank, h in enumerate(hits, 1):
        p = h.payload
        snippet = textwrap.shorten(p["text"], 170, placeholder=" ...")
        table.add_row(str(rank), f"{h.score:.4f}", p["doc_type"],
                      f"{Path(p['source_document']).name}\nchunk {p['chunk_number']} of {p['total_chunks']}", snippet)
        rows.append({"rank": rank, "score": round(h.score, 4), "doc_type": p["doc_type"],
                     "source_document": p["source_document"], "chunk_number": p["chunk_number"],
                     "title": p["title"], "text": p["text"]})
    console.print(table)
    return {"query": query, "filter": {"doc_type": doc_type} if doc_type else None, "results": rows}


def to_markdown(runs: list[dict], s) -> str:
    out = ["# SENTINEL semantic search results", "",
           f"Collection `{s.collection}` | model `{s.embed_model}` ({s.embed_dim} dims) | cosine similarity | top 5", ""]
    for i, r in enumerate(runs, 1):
        label = f"Query {i}" + (" (payload filter)" if r["filter"] else "")
        out += [f"## {label}: {r['query']}", ""]
        if r["filter"]:
            out += [f"Filter: `doc_type = {r['filter']['doc_type']}`", ""]
        out += ["| # | score | doc_type | source_document | chunk | text |", "|---|---|---|---|---|---|"]
        for h in r["results"]:
            snippet = textwrap.shorten(h["text"], 160, placeholder=" ...").replace("|", "/")
            out.append(f"| {h['rank']} | {h['score']:.4f} | {h['doc_type']} | {h['source_document']} | {h['chunk_number']} | {snippet} |")
        out.append("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query")
    ap.add_argument("--doc-type", help="payload filter, e.g. guideline, playbook, investigator_note, chargeback")
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()
    s = get_settings()
    client = get_client(s)
    embedder = get_embedder(s)
    cache = EmbeddingCache(s.cache_dir, embedder.model, embedder.dim)

    plan = [(args.query, args.doc_type)] if args.query else [(q, None) for q in QUERIES] + [FILTERED]
    vectors = embed_texts(embedder, [format_query(q) for q, _ in plan], cache, s.embed_batch_size)

    runs = []
    for i, ((q, dt), v) in enumerate(zip(plan, vectors), 1):
        console.rule(f"Search {i}/{len(plan)}" + (" (with payload filter)" if dt else ""))
        runs.append(show(client, s, v, q, dt, args.k))

    if not args.query:
        s.results_dir.mkdir(parents=True, exist_ok=True)
        (s.results_dir / "search_results.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")
        (s.results_dir / "search_results.md").write_text(to_markdown(runs, s), encoding="utf-8")
        console.print("[green]Saved[/] results/search_results.md and results/search_results.json")


if __name__ == "__main__":
    main()
