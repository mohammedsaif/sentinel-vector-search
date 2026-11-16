# Sentinel Vector Search — Video Script & Plan

## Thumbnail
`docs/screenshots/video_thumbnail.png` — dark navy background with concentric search rings, centre query dot, document points, pipeline badges (CLEAN / CHUNK / EMBED / SEARCH), title and subtitle.

---

## Video Plan (5 minutes target)

| # | Section | Duration | Visual |
|---|---------|----------|--------|
| 1 | Hook / Problem | 0:00–0:30 | Title screen → problem statement |
| 2 | What Is Sentinel | 0:30–1:00 | One-sentence intro + pipeline graphic |
| 3 | Pipeline Walkthrough | 1:00–3:00 | 4-step pipeline: Clean → Chunk → Embed → Search |
| 4 | Live Demo / Results | 3:00–4:00 | Search results from `results/search_results.md` |
| 5 | Wrap / CTA | 4:00–5:00 | Key takeaways + GitHub link |

---

## Full Script

### Section 1 — Hook (0:00–0:30)

> "Every year, millions of payment fraud cases go undetected because investigators can't search across thousands of guidelines, playbooks, and case notes fast enough.
>
> Today I'm showing you **Sentinel** — a vector search pipeline that turns raw fraud documents into a semantic knowledge base in seconds.
>
> Type your question in plain English. Get the most relevant investigative insight instantly."

### Section 2 — What Is Sentinel (0:30–1:00)

> "Sentinel is a **RAG — Retrieval Augmented Generation** pipeline built in Python.
>
> It takes raw documents — RBI guidelines, fraud playbooks, investigator notes, chargeback records — and converts them into 3,072-dimensional vectors stored in Qdrant Cloud.
>
> When you ask a natural-language question, it finds the closest matching chunks and returns ranked results with scores.
>
> Here's the four-step pipeline:"

### Section 3 — Pipeline Walkthrough (1:00–3:00)

#### Step 1: Clean (1:00–1:30)

> "Step one: **Clean**. The raw data has noise — repeated headers, footers, smart quotes, duplicates.
>
> The cleaning module strips boilerplate, normalises whitespace, and deduplicates by SHA-256 hash.
>
> What comes out is clean, structured text ready for processing."

#### Step 2: Chunk (1:30–2:00)

> "Step two: **Chunk**. Long documents get split into sentence-aware chunks — 1,000 characters each, with 200 characters of overlap.
>
> This preserves context at chunk boundaries and ensures no information is lost.
>
> Each chunk carries metadata: source file, document type, title, and chunk number."

#### Step 3: Embed (2:00–2:30)

> "Step three: **Embed**. Each chunk is converted into a 3,072-dimensional vector using Google's Gemini Embedding 2.
>
> We use asymmetric retrieval — documents get a 'search_doc' prefix, queries get a 'search_query' prefix — so the model understands the difference between stored content and search questions.
>
> Results are cached in JSONL to avoid re-embedding unchanged content."

#### Step 4: Search (2:30–3:00)

> "Step four: **Search**. Vectors are stored in a Qdrant collection using cosine distance.
>
> When you ask a question — say, 'What should I check for in a SIM swap fraud case?' — the query is embedded, then the nearest chunks are returned ranked by similarity score.
>
> You can also filter by document type — search only playbooks, only case notes, only chargebacks."

### Section 4 — Live Demo (3:00–4:00)

> "Let me show you real results.
>
> Query: *'What should an investigator check when a new device makes a large payment?'*
>
> Top result comes from our **Investigation Playbook** — score 0.85. It tells us to verify device fingerprint, cross-check with known fraud patterns, and flag for manual review.
>
> Second result is from **RBI Guidelines** — score 0.78. It cites the regulatory requirement for enhanced due diligence on high-value transactions from new devices.
>
> Query: *'How do mule accounts work in fraud networks?'*
>
> Top hit from our **Fraud Playbooks** — score 0.82. It explains the recruitment pattern, transaction velocity, and telltale signs like round-sum deposits followed by immediate digital transfers.
>
> These aren't keyword matches — these are semantic matches. The system understands meaning, not just words."

### Section 5 — Wrap Up (4:00–5:00)

> "So to recap: Sentinel takes raw fraud intelligence — guidelines, playbooks, case notes — cleans it, chunks it, embeds it into vectors, and lets you search it with natural language.
>
> Key benefits:
> - **Speed** — sub-second search across hundreds of documents
> - **Accuracy** — semantic understanding, not keyword matching
> - **Filtering** — narrow results by document type
> - **Extensible** — swap embedding providers, add new document types
>
> The full code is open-source. Clone the repo, add your .env file with a Qdrant API key, run the four scripts in order, and you have a working fraud intelligence search system.
>
> Thanks for watching."

---

## Production Notes

- **Thumbnail**: `docs/screenshots/video_thumbnail.png` (1280×720 PNG)
- **Screen recording**: Record terminal running `python scripts/health_check.py`, `python scripts/ingest.py`, `python scripts/search.py`
- **B-roll**: Pipeline graphic, code snippets from `sentinel_rag/`, search results
- **Music**: Low-volume ambient / tech background
- **Voiceover**: Calm, clear, ~130 words per minute
- **Total script**: ~850 words ≈ 5 minutes spoken
