"""Step 1: connect to Qdrant Cloud and list collections. Optionally test one embedding call.

    python scripts/health_check.py
    python scripts/health_check.py --embedding   # also check the embedding API returns 3072 dims
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from rich.console import Console  # noqa: E402
except ModuleNotFoundError:
    sys.exit(
        f"'rich' is not installed for this interpreter:\n  {sys.executable}\n"
        f"Fix with:\n  \"{sys.executable}\" -m pip install -r requirements.txt"
    )

from sentinel_rag.config import get_settings  # noqa: E402
from sentinel_rag.embeddings import format_query, get_embedder  # noqa: E402
from sentinel_rag.store import get_client  # noqa: E402

console = Console()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embedding", action="store_true", help="also make one embedding call")
    args = ap.parse_args()
    s = get_settings()

    console.rule("[bold]Qdrant health check")
    client = get_client(s)
    t0 = time.perf_counter()
    collections = client.get_collections().collections
    ms = (time.perf_counter() - t0) * 1000
    console.print(f"[green]OK[/] connected to [bold]{s.qdrant_url}[/] in {ms:.0f} ms")
    console.print(f"Collections ({len(collections)}): {[c.name for c in collections] or 'none yet'}")

    if args.embedding:
        console.rule("[bold]Embedding health check")
        emb = get_embedder(s)
        vec = emb.embed_batch([format_query("health check")])[0]
        console.print(f"[green]OK[/] provider={s.provider} model={emb.model} dimensions={len(vec)}")
        if len(vec) != s.embed_dim:
            console.print(f"[red]Expected {s.embed_dim} dimensions[/]")
            sys.exit(1)


if __name__ == "__main__":
    main()
