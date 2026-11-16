"""Cosine-search demonstration: from hand-computed 2D vectors to benchmarked HNSW.

Tasks:
  1. Reproduce the class example by hand in Python: store the 2D points
     (2,3), (1,2) and (0,4), query with (2,4), and compute the Euclidean
     distance and the cosine similarity to each point. Print the ranking for both.
  2. Write brute-force top-k search in NumPy for both metrics over the
     Gemini Embedding 2 vectors from task 4 (cached chunk embeddings).
  3. Run the same queries in Qdrant and show that the results match your
     NumPy results.
  4. Normalise the vectors and show why cosine and dot product then give
     the same ranking.
  5. Time brute force against Qdrant for 1,000 and for 10,000 vectors,
     and explain in the README what an HNSW index changes.

Run:
    python scripts/cosine_search.py                 # real cached Gemini vectors + real queries, local Qdrant
    python scripts/cosine_search.py --cloud         # tasks 3 and 5 on Qdrant Cloud (QDRANT_URL/KEY from .env)
    python scripts/cosine_search.py --source random # no API key / cache needed
    python scripts/cosine_search.py --qdrant-url http://localhost:6333   # self-hosted server
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient, models

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEED = 42  # reproducible random vectors
COLLECTION = "cosine-demo"


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D arrays."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


# ---------------------------------------------------------------------------
# Task 1 — Hand-compute on 2D points
# ---------------------------------------------------------------------------

def task1() -> None:
    print("=" * 70)
    print("TASK 1 — Hand-compute Euclidean distance & cosine similarity (2D)")
    print("=" * 70)

    points = {
        "A": np.array([2.0, 3.0]),
        "B": np.array([1.0, 2.0]),
        "C": np.array([0.0, 4.0]),
    }
    query = np.array([2.0, 4.0])
    print(f"Query vector: {query.tolist()}")
    print(f"Stored points: {', '.join(f'{k}={v.tolist()}' for k, v in points.items())}")
    print()

    euclidean: dict[str, float] = {}
    cosine: dict[str, float] = {}

    for name, p in points.items():
        euclidean[name] = euclidean_distance(query, p)
        cosine[name] = cosine_similarity(query, p)

    print("  Euclidean distances (smaller = closer):")
    for name, p in points.items():
        d = euclidean[name]
        print(f"    {name} {p.tolist()}  →  |{query.tolist()} - {p.tolist()}| = {d:.6f}")

    print()
    print("  Cosine similarity (larger = more aligned):")
    for name, p in points.items():
        dot = float(np.dot(query, p))
        norm_q = np.linalg.norm(query)
        norm_p = np.linalg.norm(p)
        cs = cosine[name]
        print(f"    {name} {p.tolist()}  →  ({query.tolist()}·{p.tolist()}) / (|q|·|p|) = {dot} / ({norm_q:.6f} × {norm_p:.6f}) = {cs:.6f}")

    print()
    euclidean_ranked = sorted(euclidean.items(), key=lambda x: x[1])
    cosine_ranked = sorted(cosine.items(), key=lambda x: x[1], reverse=True)

    print("  Euclidean ranking (closest first):")
    for i, (name, d) in enumerate(euclidean_ranked, 1):
        print(f"    {i}. {name}  ({d:.6f})")

    print()
    print("  Cosine ranking (most aligned first):")
    for i, (name, cs) in enumerate(cosine_ranked, 1):
        print(f"    {i}. {name}  ({cs:.6f})")

    print()
    euc_order = [n for n, _ in euclidean_ranked]
    cos_order = [n for n, _ in cosine_ranked]
    print(f"  Observation: Euclidean order = {' > '.join(euc_order)}, cosine order = {' > '.join(cos_order)}.")
    if euc_order != cos_order:
        print(f"  The metrics DISAGREE: {euc_order[0]} is nearest by distance, but {cos_order[0]} "
              f"points in the same direction as the query")
        print(f"  (cosine = {cosine[cos_order[0]]:.6f}) while ranking #{euc_order.index(cos_order[0]) + 1} by distance.")
        print("  Cosine ignores vector length and compares direction only.")
    else:
        print("  Both metrics agree on the ranking.")
    print()


# ---------------------------------------------------------------------------
# Task 2 — Brute-force top-k in NumPy (both metrics)
# ---------------------------------------------------------------------------

def brute_force_cosine(vectors: np.ndarray, query: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (indices, similarities) for top-k by cosine similarity."""
    sims = vectors @ query / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(query))
    top_idx = np.argsort(sims)[::-1][:k]
    return top_idx, sims[top_idx]


def brute_force_euclidean(vectors: np.ndarray, query: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (indices, distances) for top-k by Euclidean distance."""
    dists = np.linalg.norm(vectors - query, axis=1)
    top_idx = np.argsort(dists)[:k]
    return top_idx, dists[top_idx]


def task2(vectors: np.ndarray, queries: np.ndarray) -> None:
    k = 5
    print("=" * 70)
    print(f"TASK 2 — Brute-force top-{k} in NumPy (Euclidean & Cosine)")
    print("=" * 70)
    print(f"  {len(vectors)} vectors of dimension {vectors.shape[1]}")
    print(f"  {len(queries)} query vectors")
    print()

    for q_idx, q in enumerate(queries):
        cos_idx, cos_sim = brute_force_cosine(vectors, q, k)
        euc_idx, euc_dist = brute_force_euclidean(vectors, q, k)

        print(f"  Query {q_idx + 1} cosine top-{k}:")
        for i, (idx, sim) in enumerate(zip(cos_idx, cos_sim), 1):
            print(f"    {i}. vector {idx:4d}  cos_sim = {sim:.6f}")

        print(f"  Query {q_idx + 1} euclidean top-{k}:")
        for i, (idx, dist) in enumerate(zip(euc_idx, euc_dist), 1):
            print(f"    {i}. vector {idx:4d}  euclidean = {dist:.6f}")
        print()


# ---------------------------------------------------------------------------
# Task 3 — Verify NumPy matches Qdrant
# ---------------------------------------------------------------------------

def _connect(url: str | None, api_key: str | None) -> QdrantClient:
    if url:
        return QdrantClient(url=url, api_key=api_key, timeout=120)
    return QdrantClient(location=":memory:")


def _fresh_collection(
    client: QdrantClient, name: str, size: int, distance: models.Distance,
    hnsw: models.HnswConfigDiff | None = None,
    optimizers: models.OptimizersConfigDiff | None = None,
) -> None:
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(size=size, distance=distance, hnsw_config=hnsw),
        optimizers_config=optimizers,
    )


def _upsert_all(client: QdrantClient, name: str, vectors: np.ndarray, batch: int = 500) -> None:
    for start in range(0, len(vectors), batch):
        client.upsert(
            collection_name=name,
            points=[
                models.PointStruct(id=start + j, vector=v.tolist())
                for j, v in enumerate(vectors[start:start + batch])
            ],
            wait=True,
        )


def task3(vectors: np.ndarray, queries: np.ndarray,
          url: str | None = None, api_key: str | None = None) -> None:
    k = 5
    print("=" * 70)
    print("TASK 3 — Match NumPy with Qdrant (COSINE and EUCLID collections)")
    print("=" * 70)
    where = f"Qdrant server {url}" if url else ":memory: Qdrant (local mode)"
    print(f"  {len(vectors)} vectors of dimension {vectors.shape[1]} in {where}")
    print("  Queries use exact=True so the comparison is exact, not approximate.")
    print()

    client = _connect(url, api_key)
    # (label, Qdrant distance, NumPy implementation, what the score means)
    checks = (
        ("COSINE", models.Distance.COSINE, brute_force_cosine, "similarity"),
        ("EUCLID", models.Distance.EUCLID, brute_force_euclidean, "distance"),
    )
    all_match = True
    for label, distance, numpy_fn, meaning in checks:
        name = f"{COLLECTION}-t3-{label.lower()}"
        _fresh_collection(client, name, vectors.shape[1], distance)
        _upsert_all(client, name, vectors)
        print(f"  {label} ({meaning})")
        try:
            for q_idx, q in enumerate(queries):
                np_idx, np_scores = numpy_fn(vectors, q, k)
                res = client.query_points(
                    collection_name=name, query=q.tolist(), limit=k,
                    search_params=models.SearchParams(exact=True) if url else None,
                ).points
                qd_idx = np.array([int(p.id) for p in res])
                qd_scores = np.array([p.score for p in res])

                idx_match = np.array_equal(np_idx, qd_idx)
                score_close = np.allclose(np_scores, qd_scores, atol=1e-4)
                ok = idx_match and score_close
                all_match = all_match and ok
                print(f"    Query {q_idx + 1}  {'✓' if ok else '✗'}  "
                      f"(ids match={idx_match}, {meaning} match={score_close})")
                if not ok:
                    print(f"      NumPy:  ids={np_idx.tolist()} scores={np_scores.tolist()}")
                    print(f"      Qdrant: ids={qd_idx.tolist()} scores={qd_scores.tolist()}")
        finally:
            client.delete_collection(name)  # our own scratch collection
        print()

    if all_match:
        print("  NumPy MATCHES Qdrant for both metrics (same ordered IDs, scores within 1e-4).")
    else:
        print("  MISMATCH between NumPy and Qdrant — see the ✗ rows above.")
    if not url:
        print("  (Local mode runs NumPy inside qdrant-client; use --cloud for a server-side check.)")
    print()


# ---------------------------------------------------------------------------
# Task 4 — Normalised vectors: cosine == dot product
# ---------------------------------------------------------------------------

def normalise(vectors: np.ndarray) -> np.ndarray:
    """L2-normalise every row to unit length."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)  # guard against zero vectors
    return vectors / norms


def task4(vectors: np.ndarray, queries: np.ndarray) -> None:
    k = 5
    print("=" * 70)
    print("TASK 4 — Normalised vectors: cosine = dot product")
    print("=" * 70)

    norm_vectors = normalise(vectors)
    norm_queries = normalise(queries)

    for q_idx, (q, nq) in enumerate(zip(queries, norm_queries)):
        # Cosine on raw data
        cos_idx, cos_sim = brute_force_cosine(vectors, q, k)

        # Dot product on normalised data
        dot_scores = norm_vectors @ nq  # for unit vectors, dot = cosine
        dot_idx = np.argsort(dot_scores)[::-1][:k]
        dot_sim = dot_scores[dot_idx]

        idx_match = np.array_equal(cos_idx, dot_idx)
        sim_close = np.allclose(cos_sim, dot_sim, atol=1e-6)

        status = "✓" if (idx_match and sim_close) else "✗"
        print(f"  Query {q_idx + 1}  {status}  (idx match={idx_match}, sim match={sim_close})")

        if sim_close:
            print(f"    Cosine (raw):   {cos_sim.tolist()}")
            print(f"    Dot (norm):     {dot_sim.tolist()}")
        else:
            print(f"    Cosine (raw):   {cos_sim.tolist()}")
            print(f"    Dot (norm):     {dot_sim.tolist()}")

    print()
    print("  When vectors are L2-normalised to unit length:")
    print("    a·b / (|a||b|) = a·b / (1·1) = a·b")
    print("  So cosine similarity collapses to the plain dot product.")
    print("  The ranking is identical.")
    print()


# ---------------------------------------------------------------------------
# Task 5 — Benchmark brute force vs Qdrant
# ---------------------------------------------------------------------------

MIN_INDEX_COVERAGE = 0.90  # share of vectors that must be in the HNSW graph before timing


def _wait_indexed(client: QdrantClient, name: str, n_points: int, timeout_s: int = 600) -> float:
    """Wait for GREEN status AND for the vectors to actually be indexed.

    GREEN only means the optimizers are idle. A collection below the indexing
    threshold is GREEN with no graph at all, so also check indexed_vectors_count.
    Raises instead of silently benchmarking an unindexed collection.
    """
    deadline = time.time() + timeout_s
    status, indexed = None, 0
    while time.time() < deadline:
        info = client.get_collection(name)
        status, indexed = info.status, info.indexed_vectors_count or 0
        if (status == models.CollectionStatus.GREEN
                and (info.points_count or 0) == n_points
                and indexed >= MIN_INDEX_COVERAGE * n_points):
            return indexed / n_points
        time.sleep(1)
    raise RuntimeError(
        f"{name}: not indexed after {timeout_s}s (status={status}, indexed={indexed}/{n_points}). "
        "HNSW timings would be meaningless, so the benchmark stops here."
    )


def _round_trip(client: QdrantClient, name: str, repeats: int = 10) -> float:
    """Median latency of a trivial call: the cost of the network, not of the search."""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        client.count(collection_name=name)
        times.append(time.perf_counter() - t0)
    return float(np.median(times))


def task5(dim: int = 3072, qdrant_url: str | None = None, api_key: str | None = None,
          keep: bool = False) -> None:
    print("=" * 70)
    print("TASK 5 — Benchmark: NumPy brute-force vs Qdrant")
    print("=" * 70)
    print(f"  Dimension: {dim}   (random Gaussian vectors: 10,000 real embeddings do not exist)")
    if qdrant_url:
        print(f"  Qdrant: server at {qdrant_url}")
        print("  HNSW collection: m=16, ef_construct=100, indexing_threshold=1000 KB")
        print("  (default threshold is 20,000 KB ≈ 1,666 vectors of 3072 dims, so 1,000 vectors")
        print("   would never get a graph by default)")
        print("  'Exact' = same collection queried with exact=True (graph bypassed)")
    else:
        print("  Qdrant: local :memory: mode. NOTE: local mode does NOT build an HNSW")
        print("  graph — it scans every vector, so Qdrant timings below are brute force.")
        print("  Pass --cloud or --qdrant-url for a true HNSW test.")
    print()

    sizes = [1_000, 10_000]
    n_queries = 10
    k = 5
    ef = 128
    rng = np.random.RandomState(SEED)

    for n_vectors in sizes:
        print(f"  --- {n_vectors} vectors ---")
        vectors = rng.randn(n_vectors, dim).astype(np.float32)
        query_set = rng.randn(n_queries, dim).astype(np.float32)

        t0 = time.perf_counter()
        for q in query_set:
            brute_force_cosine(vectors, q, k)
        tf_brute = time.perf_counter() - t0

        t0 = time.perf_counter()
        for q in query_set:
            brute_force_euclidean(vectors, q, k)
        tf_euc = time.perf_counter() - t0

        name = f"{COLLECTION}-hnsw"
        client = _connect(qdrant_url, api_key)
        _fresh_collection(
            client, name, dim, models.Distance.COSINE,
            hnsw=models.HnswConfigDiff(m=16, ef_construct=100),
            optimizers=models.OptimizersConfigDiff(indexing_threshold=1000) if qdrant_url else None,
        )
        try:
            t0 = time.perf_counter()
            _upsert_all(client, name, vectors)
            coverage = _wait_indexed(client, name, n_vectors) if qdrant_url else 0.0
            t_build = time.perf_counter() - t0
            rtt = _round_trip(client, name)

            # local mode ignores search_params (and warns), so only send them to a server
            approx = models.SearchParams(hnsw_ef=ef, exact=False) if qdrant_url else None
            exact = models.SearchParams(exact=True) if qdrant_url else None

            def run(params: models.SearchParams | None) -> tuple[float, list[list[int]]]:
                hits: list[list[int]] = []
                start = time.perf_counter()
                for q in query_set:
                    res = client.query_points(
                        collection_name=name, query=q.tolist(), limit=k, search_params=params
                    ).points
                    hits.append([int(p.id) for p in res])
                return time.perf_counter() - start, hits

            tf_approx, approx_hits = run(approx)
            tf_exact, exact_hits = run(exact)
        finally:
            if qdrant_url and not keep:
                client.delete_collection(name)  # our own scratch collection

        overlap_approx = overlap_exact = 0
        for q, a_hits, e_hits in zip(query_set, approx_hits, exact_hits):
            truth = set(brute_force_cosine(vectors, q, k)[0].tolist())
            overlap_approx += len(truth & set(a_hits))
            overlap_exact += len(truth & set(e_hits))
        recall_approx = overlap_approx / (n_queries * k)
        recall_exact = overlap_exact / (n_queries * k)

        per = lambda t: t / n_queries  # noqa: E731
        print(f"    NumPy brute-force cosine:     {per(tf_brute):.4f}s per query")
        print(f"    NumPy brute-force euclidean:  {per(tf_euc):.4f}s per query")
        print(f"    Qdrant exact=True (scan):     {per(tf_exact):.4f}s per query   recall@{k} {recall_exact:.2f}")
        label = "Qdrant HNSW (ef=%d):" % ef if qdrant_url else "Qdrant local (no graph):"
        print(f"    {label:<30}{per(tf_approx):.4f}s per query   recall@{k} {recall_approx:.2f}")
        if qdrant_url:
            print(f"    Network round trip (count):   {rtt:.4f}s  | build+index {t_build:.1f}s"
                  f" | indexed {coverage:.1%} of vectors")
            net_exact, net_hnsw = max(per(tf_exact) - rtt, 0.0), max(per(tf_approx) - rtt, 0.0)
            print(f"    Minus round trip:  exact {net_exact:.4f}s  HNSW {net_hnsw:.4f}s")
            if per(tf_approx) > 0:
                print(f"    exact / HNSW wall-clock: {tf_exact / tf_approx:.2f}x")
        print()

    print("  What HNSW changes:")
    print("  - Exact scan (NumPy or exact=True) compares EVERY vector → O(n) per query.")
    print("  - HNSW builds a multi-layer graph: sparse top layers (long hops), dense bottom.")
    print("    A query descends greedily and only visits a small neighbourhood → ~O(log n).")
    print("  - Trade-offs: build time, extra memory, and APPROXIMATE results (recall < 1.0).")
    print("  - Only the numbers printed above are measurements; speed-ups depend on n, dimension,")
    print("    data distribution and network distance. Random vectors are a hard case for recall.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

QUERY_TEXTS = [
    "What should an investigator check when a new device makes a large payment?",
    "How do mule accounts work in fraud networks?",
    "What should I check for in a SIM swap fraud case?",
]


def generate_vectors(n: int, dim: int, seed: int = SEED) -> np.ndarray:
    """Generate random unit-norm vectors (simulating embedding direction)."""
    rng = np.random.RandomState(seed)
    vectors = rng.randn(n, dim).astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


def use_fake_embedder(n: int, dim: int) -> np.ndarray:
    """Use the project's FakeEmbedder to generate vectors."""
    from sentinel_rag.config import Settings
    from sentinel_rag.embeddings import FakeEmbedder

    settings = replace(Settings(), embed_dim=dim, provider="fake")  # Settings is frozen
    embedder = FakeEmbedder(settings)

    texts = [f"sample document {i} with some words for embedding {i}" for i in range(n)]
    vectors = embedder.embed_batch(texts)
    return np.array(vectors, dtype=np.float32)


def load_gemini_vectors(n_max: int | None) -> tuple[np.ndarray, np.ndarray]:
    """Real Gemini vectors: cached chunk embeddings + the same model embedding real queries.

    Documents come from the embedding cache that scripts/ingest.py filled (keyed by the
    exact "title: ... | text: ..." string), so no document is re-embedded or re-paid for.
    Queries use the asymmetric query prefix and are cached in the same file.
    """
    from sentinel_rag.config import get_settings
    from sentinel_rag.embeddings import (
        EmbeddingCache, embed_texts, format_document, format_query, get_embedder,
    )

    s = get_settings()
    chunks_path = s.processed_dir / "chunks.jsonl"
    if not chunks_path.exists():
        raise SystemExit(f"{chunks_path} not found. Run scripts/ingest.py first, or use --source random.")
    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines()]
    cache = EmbeddingCache(s.cache_dir, s.embed_model, s.embed_dim)

    vectors = [v for c in chunks if (v := cache.get(format_document(c["title"], c["text"]))) is not None]
    missing = len(chunks) - len(vectors)
    if not vectors:
        raise SystemExit(f"No cached {s.embed_model} vectors in {cache.path}. Run scripts/ingest.py first.")
    if n_max:
        vectors = vectors[:n_max]
    print(f"  {len(vectors)} cached {s.embed_model} chunk vectors from {cache.path.name}"
          f"{f' ({missing} chunks not cached, skipped)' if missing else ''}")

    embedder = get_embedder(s)  # needs GEMINI_API_KEY only for queries not yet cached
    queries = embed_texts(embedder, [format_query(q) for q in QUERY_TEXTS], cache, batch_size=16)
    for i, q in enumerate(QUERY_TEXTS, 1):
        print(f"  Query {i}: {q}")
    return np.array(vectors, dtype=np.float32), np.array(queries, dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cosine-search demo")
    parser.add_argument("--source", choices=["gemini", "random", "fake"], default="gemini",
                        help="vectors for tasks 2-4: cached Gemini embeddings (default), "
                             "random unit vectors, or the project's FakeEmbedder")
    parser.add_argument("--n-vectors", type=int, default=None,
                        help="vectors for tasks 2-4 (gemini: all cached; random/fake: 100)")
    parser.add_argument("--dim", type=int, default=3072,
                        help="Vector dimension (Gemini Embedding 2)")
    parser.add_argument("--qdrant-url", default=None,
                        help="Qdrant server URL for tasks 3 and 5; default is local :memory: mode")
    parser.add_argument("--cloud", action="store_true",
                        help="Use Qdrant Cloud: QDRANT_URL / QDRANT_API_KEY from .env")
    parser.add_argument("--keep-collections", action="store_true",
                        help="do not delete the cosine-demo-* scratch collections after task 5")
    args = parser.parse_args()

    api_key: str | None = None
    if args.cloud:
        from sentinel_rag.config import Settings
        cfg = Settings()
        if not cfg.qdrant_url:
            parser.error("--cloud needs QDRANT_URL in .env (copy .env.example)")
        args.qdrant_url, api_key = cfg.qdrant_url, cfg.qdrant_api_key

    print("Sentinel — Cosine-Search Demonstration")
    print("─" * 70)
    print()

    # Task 1 (pure 2D, no vectors needed)
    task1()

    # Vectors for tasks 2–4
    if args.source == "gemini":
        print("Loading real Gemini vectors…")
        vectors, queries = load_gemini_vectors(args.n_vectors)
        args.dim = vectors.shape[1]
        print()
    else:
        n = args.n_vectors or 100
        if args.source == "fake":
            print("Generating vectors with FakeEmbedder…")
            vectors = use_fake_embedder(n, args.dim)
        else:
            print(f"Generating {n} random unit-norm vectors (dim={args.dim})…")
            vectors = generate_vectors(n, args.dim)
        queries = generate_vectors(3, args.dim, seed=SEED + 99)

    task2(vectors, queries)
    task3(vectors, queries, args.qdrant_url, api_key)
    task4(vectors, queries)

    # Task 5 (benchmark with its own vectors)
    task5(args.dim, args.qdrant_url, api_key, keep=args.keep_collections)

    print("=" * 70)
    print("All tasks complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
