"""Cosine-search demonstration: from hand-computed 2D vectors to benchmarked HNSW.

Tasks:
  1. Reproduce the class example by hand in Python: store the 2D points
     (2,3), (1,2) and (0,4), query with (2,4), and compute the Euclidean
     distance and the cosine similarity to each point. Print the ranking for both.
  2. Write brute-force top-k search in NumPy for both metrics over the
     Gemini Embedding 2 vectors from task 4 (or 1,000 new ones).
  3. Run the same queries in Qdrant and show that the results match your
     NumPy results.
  4. Normalise the vectors and show why cosine and dot product then give
     the same ranking.
  5. Time brute force against Qdrant for 1,000 and for 10,000 vectors,
     and explain in the README what an HNSW index changes.

Run:
    python scripts/cosine_search.py              # uses :memory: Qdrant + random vectors
    python scripts/cosine_search.py --use-fake   # uses project's FakeEmbedder for vectors
    python scripts/cosine_search.py --cloud      # task 5 on Qdrant Cloud (QDRANT_URL/KEY from .env)
    python scripts/cosine_search.py --qdrant-url http://localhost:6333  # task 5 on a self-hosted server
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace

import numpy as np
from qdrant_client import QdrantClient, models

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

def task3(vectors: np.ndarray, queries: np.ndarray) -> None:
    k = 5
    print("=" * 70)
    print("TASK 3 — Match NumPy cosine with Qdrant COSINE distance")
    print("=" * 70)
    print(f"  {len(vectors)} vectors of dimension {vectors.shape[1]} in :memory: Qdrant")
    print()

    # Build in-memory Qdrant collection with COSINE distance
    client = QdrantClient(location=":memory:")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=models.VectorParams(
            size=vectors.shape[1],
            distance=models.Distance.COSINE,
        ),
    )

    points = [
        models.PointStruct(id=int(i), vector=v.tolist())
        for i, v in enumerate(vectors)
    ]
    client.upsert(collection_name=COLLECTION, points=points, wait=True)

    all_match = True

    for q_idx, q in enumerate(queries):
        # NumPy top-k cosine (sorted by similarity descending)
        cos_idx, cos_sim = brute_force_cosine(vectors, q, k)

        # Qdrant search (returns sorted by COSINE distance ascending)
        qr = client.query_points(
            collection_name=COLLECTION,
            query=q.tolist(),
            limit=k,
        ).points

        qr_idx = np.array([int(p.id) for p in qr])
        # Qdrant COSINE distance returns cosine similarity (higher = closer)
        qr_cos_sim = np.array([p.score for p in qr])

        idx_match = np.array_equal(cos_idx, qr_idx)
        sim_close = np.allclose(cos_sim, qr_cos_sim, atol=1e-3)

        status = "✓" if (idx_match and sim_close) else ("~" if sim_close else "✗")
        if not (idx_match and sim_close):
            all_match = False

        print(f"  Query {q_idx + 1}  {status}")
        if not idx_match:
            print(f"    NumPy indices:  {cos_idx.tolist()}")
            print(f"    Qdrant indices: {qr_idx.tolist()}")
        if not sim_close:
            print(f"    NumPy sims:  {cos_sim.tolist()}")
            print(f"    Qdrant sims (score):  {qr_cos_sim.tolist()}")

    print()
    if all_match:
        print("  All queries: NumPy cosine rankings MATCH Qdrant (same IDs, scores within 1e-3).")
    else:
        print("  Some queries differed in IDs or scores beyond tolerance (see above).")
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

def _build_collection(
    url: str | None, name: str, vectors: np.ndarray, hnsw: models.HnswConfigDiff,
    api_key: str | None = None,
) -> QdrantClient:
    """Create a fresh collection, upsert in batches and wait until it is indexed."""
    client = (
        QdrantClient(url=url, api_key=api_key, timeout=120)
        if url else QdrantClient(location=":memory:")
    )
    if url and client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(
            size=vectors.shape[1], distance=models.Distance.COSINE, hnsw_config=hnsw
        ),
    )
    batch = 500
    for start in range(0, len(vectors), batch):
        chunk = vectors[start:start + batch]
        client.upsert(
            collection_name=name,
            points=[
                models.PointStruct(id=start + j, vector=v.tolist())
                for j, v in enumerate(chunk)
            ],
            wait=True,
        )
    if url:  # a server builds the HNSW graph in the background
        deadline = time.time() + 300
        while time.time() < deadline:
            if client.get_collection(name).status == models.CollectionStatus.GREEN:
                break
            time.sleep(0.5)
    return client


def task5(dim: int = 3072, qdrant_url: str | None = None, api_key: str | None = None) -> None:
    print("=" * 70)
    print("TASK 5 — Benchmark: NumPy brute-force vs Qdrant")
    print("=" * 70)
    print(f"  Dimension: {dim}")
    if qdrant_url:
        print(f"  Qdrant: server at {qdrant_url} (real HNSW index)")
    else:
        print("  Qdrant: local :memory: mode. NOTE: local mode does NOT build an HNSW")
        print("  graph — it scans every vector, so Qdrant timings below are brute force.")
        print("  Pass --qdrant-url http://localhost:6333 (or a Cloud URL) for a true HNSW test.")
    print()

    sizes = [1_000, 10_000]
    n_queries = 10
    k = 5
    rng = np.random.RandomState(SEED)

    for n_vectors in sizes:
        print(f"  --- {n_vectors} vectors ---")

        # Generate random vectors
        vectors = rng.randn(n_vectors, dim).astype(np.float32)
        query_set = rng.randn(n_queries, dim).astype(np.float32)

        # ---- Brute force cosine ----
        t0 = time.perf_counter()
        for q in query_set:
            brute_force_cosine(vectors, q, k)
        tf_brute = time.perf_counter() - t0

        # ---- Brute force euclidean ----
        t0 = time.perf_counter()
        for q in query_set:
            brute_force_euclidean(vectors, q, k)
        tf_euc = time.perf_counter() - t0

        # ---- Qdrant (with HNSW index) ----
        client = _build_collection(
            qdrant_url, f"{COLLECTION}-hnsw", vectors,
            models.HnswConfigDiff(m=16, ef_construct=100), api_key,
        )
        t0 = time.perf_counter()
        hnsw_hits: list[list[int]] = []
        for q in query_set:
            res = client.query_points(
                collection_name=f"{COLLECTION}-hnsw", query=q.tolist(), limit=k
            ).points
            hnsw_hits.append([int(p.id) for p in res])
        tf_qdrant = time.perf_counter() - t0

        # ---- Qdrant flat (HNSW graph disabled with m=0) ----
        client_flat = _build_collection(
            qdrant_url, f"{COLLECTION}-flat", vectors, models.HnswConfigDiff(m=0), api_key
        )
        t0 = time.perf_counter()
        for q in query_set:
            client_flat.query_points(
                collection_name=f"{COLLECTION}-flat", query=q.tolist(), limit=k
            )
        tf_flat = time.perf_counter() - t0

        # ---- Recall of the Qdrant (HNSW) results against exact NumPy cosine ----
        overlap = 0
        for q, hits in zip(query_set, hnsw_hits):
            exact_idx, _ = brute_force_cosine(vectors, q, k)
            overlap += len(set(exact_idx.tolist()) & set(hits))
        recall = overlap / (n_queries * k)

        print(f"    NumPy brute-force cosine:    {tf_brute:.4f}s  ({tf_brute / n_queries:.4f}s per query)")
        print(f"    NumPy brute-force euclidean: {tf_euc:.4f}s  ({tf_euc / n_queries:.4f}s per query)")
        print(f"    Qdrant (m=16 graph):         {tf_qdrant:.4f}s  ({tf_qdrant / n_queries:.4f}s per query)")
        print(f"    Qdrant (m=0, no graph):      {tf_flat:.4f}s  ({tf_flat / n_queries:.4f}s per query)")
        print(f"    Recall@{k} of Qdrant vs exact NumPy: {recall:.2f}")

        if tf_qdrant > 0:
            label = "HNSW" if qdrant_url else "local-mode Qdrant"
            print(f"    NumPy brute-force / {label}: {tf_brute / tf_qdrant:.2f}x")
            print(f"    Qdrant flat / {label}:       {tf_flat / tf_qdrant:.2f}x")
        print()

    print("  Why HNSW helps:")
    print("  - Brute-force (and flat Qdrant) check EVERY vector → O(n) per query.")
    print("  - HNSW (Hierarchical Navigable Small World) builds a multi-layer")
    print("    graph: top layers are sparse (long hops), bottom layers are dense.")
    print("  - A query starts at the top, skips irrelevant clusters, and drills")
    print("    down only into the nearest region → sub-linear search ~O(log n).")
    print("  - Trade-off: build time and memory for the graph, and approximate")
    print("    results (recall can be < 1.0). The gap grows with collection size.")
    if not qdrant_url:
        print("  - These numbers came from local mode (no graph); rerun with")
        print("    --qdrant-url to measure a real HNSW speed-up.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Cosine-search demo")
    parser.add_argument("--use-fake", action="store_true",
                        help="Use project FakeEmbedder instead of random vectors")
    parser.add_argument("--n-vectors", type=int, default=100,
                        help="Number of vectors for tasks 2–4")
    parser.add_argument("--dim", type=int, default=3072,
                        help="Vector dimension (Gemini Embedding 2)")
    parser.add_argument("--qdrant-url", default=None,
                        help="Qdrant server URL for task 5 (real HNSW); default is local :memory: mode")
    parser.add_argument("--cloud", action="store_true",
                        help="Task 5 on Qdrant Cloud, using QDRANT_URL / QDRANT_API_KEY from .env")
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

    # Generate vectors for tasks 2–5
    if args.use_fake:
        print("Generating vectors with FakeEmbedder…")
        vectors = use_fake_embedder(args.n_vectors, args.dim)
    else:
        print(f"Generating {args.n_vectors} random unit-norm vectors (dim={args.dim})…")
        vectors = generate_vectors(args.n_vectors, args.dim)

    queries = generate_vectors(3, args.dim, seed=SEED + 99)

    # Tasks 2–4
    task2(vectors, queries)
    task3(vectors, queries)
    task4(vectors, queries)

    # Task 5 (benchmark with its own vectors)
    task5(args.dim, args.qdrant_url, api_key)

    print("=" * 70)
    print("All tasks complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
