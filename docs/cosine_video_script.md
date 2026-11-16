# cosine_search.py — Video Script (about 5 minutes)

Visuals: `docs/cosine_intro_poster.html` (opening card) and the Excalidraw notes diagram (walk through it left to right while narrating).

| # | Section | Time | On screen |
|---|---------|------|-----------|
| 1 | Hook | 0:00–0:30 | Poster |
| 2 | Task 1: 2D by hand | 0:30–1:45 | Excalidraw plot + terminal |
| 3 | Tasks 2–3: NumPy vs Qdrant | 1:45–2:45 | Terminal output |
| 4 | Task 4: Normalise | 2:45–3:30 | Terminal + formula |
| 5 | Task 5: HNSW benchmark | 3:30–4:30 | Terminal + HNSW box |
| 6 | Wrap | 4:30–5:00 | Poster |

## 1. Hook (0:00–0:30)

> "When Sentinel searches fraud playbooks, it isn't comparing words. It's comparing directions in a 3,072-dimensional space.
> Today I'll show why the ruler we use matters — cosine similarity versus plain distance — and how a vector database makes it fast.
> Everything runs from one script: `cosine_search.py`."

## 2. Task 1 — 2D by hand (0:30–1:45)

*Run `python scripts/cosine_search.py`; point at the Task 1 block.*

> "Three stored points: A at 2,3. B at 1,2. C at 0,4. The query is 2,4.
> By Euclidean distance, A wins at 1.0. C is next at 2.0. B is last at 2.24.
> Now cosine: dot product divided by the two lengths. B scores exactly 1.0, because B points along the same line as the query. A is 0.992. C is 0.894.
> Same data, two rulers, **different winners**. B goes from last to first.
> That's the point. Embeddings put meaning in direction, not length — so for text, cosine is the right question."

*The script's closing 'Observation' line for Task 1 now prints the real result (Euclidean A > C > B, cosine B > A > C), so you can read it on screen.*

## 3. Tasks 2–3 — NumPy vs Qdrant (1:45–2:45)

> "Task two is brute force. One matrix multiply scores every vector against the query, `argsort` picks the top five. We do it for cosine and for Euclidean.
> Task three sends the same queries to Qdrant with `Distance.COSINE`. The IDs and scores match NumPy. So the database isn't magic — it's the same math, packaged with an index."

## 4. Task 4 — Normalise (2:45–3:30)

> "If every vector has length one, the denominator in the cosine formula is one times one. Cosine collapses to a plain dot product.
> The script normalises the vectors, takes dot products, and the ranking is identical to raw cosine.
> Why bother? A dot product skips the square roots and the division — cheaper at scale. That's why many embedding models return unit vectors."

## 5. Task 5 — Benchmark and HNSW (3:30–4:30)

> "Now speed. We time 1,000 and 10,000 vectors, 3,072 dimensions each: NumPy brute force against Qdrant.
> Brute force checks every vector — linear in n. HNSW builds a layered graph. The top layers are sparse with long hops; the bottom is dense. A query enters at the top, jumps toward the target, and drills down only into the nearest neighborhood. Roughly logarithmic.
> The trade-off: build time and memory for the graph, and results that are approximate, not guaranteed exact."

*Measured results (Qdrant Cloud, sa-east-1, 3072-dim random vectors, 10 queries): NumPy brute force 0.005 s/query at 1k and 0.047 s/query at 10k. Qdrant Cloud was about 0.40 s/query for both HNSW and no-graph, at both sizes, because the network round trip dominates. Recall@5 was 1.00 at 1k and 0.38 at 10k (random vectors have no cluster structure, which is the worst case for HNSW). So this run does NOT show an HNSW speedup; say so on camera, and explain that the benefit appears at much larger collections, close to the server, with real embeddings. Do not claim a speedup from these numbers.*

*Older note: record this section twice if you can. Default run (`:memory:`) is Qdrant's local mode, which does not build an HNSW graph. On our run it was slower than NumPy (about 0.4x at 10,000 vectors), and the script prints that warning. For the real HNSW numbers run `python scripts/cosine_search.py --qdrant-url http://localhost:6333`; it also prints recall@5 against exact NumPy results. Only quote speedups from that run.*

## 6. Wrap (4:30–5:00)

> "Recap: cosine measures direction. NumPy and Qdrant agree. Normalise and cosine becomes a dot product. HNSW trades a little exactness for a lot of speed.
> Code is in `scripts/cosine_search.py`. Thanks for watching."

## Production notes

- Voiceover about 130 words per minute; script is roughly 600 words.
- Record terminal at 1080p, font size 18+.
- Zoom the Excalidraw diagram into the 2D plot for section 2, then the Task 2–5 row for sections 3–5.
