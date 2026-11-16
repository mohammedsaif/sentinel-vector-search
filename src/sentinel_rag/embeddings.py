"""Embedding providers for Gemini Embedding 2 (3072 dimensions).

Two things about gemini-embedding-2 that this module handles:

1. It does NOT take a `task_type` field. The task goes into the text as a
   prefix. For asymmetric retrieval Google documents:
       query:    "task: search result | query: {text}"
       document: "title: {title} | text: {text}"
2. Passing a plain list of strings to embed_content returns ONE aggregated
   vector for the whole list. To get one vector per chunk, each chunk must be
   sent as its own `types.Content` object.

Providers
- google : Google Gemini API via the google-genai SDK (GEMINI_API_KEY)
- euri   : Euron EURI gateway, which exposes an OpenAI-compatible
           /embeddings endpoint (EURI_API_KEY, EURI_BASE_URL)
- fake   : offline hashed bag-of-words vectors, ONLY for tests and dry runs
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from pathlib import Path
from typing import Protocol

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .config import Settings


def format_document(title: str, text: str) -> str:
    return f"title: {title or 'none'} | text: {text}"


def format_query(query: str) -> str:
    return f"task: search result | query: {query}"


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(s in msg for s in ("429", "resource_exhausted", "rate", "quota", "503", "unavailable", "timeout", "deadline"))


_retry = retry(retry=retry_if_exception(_is_retryable), wait=wait_exponential(multiplier=2, min=2, max=60),
               stop=stop_after_attempt(8), reraise=True)


class Embedder(Protocol):
    model: str
    dim: int

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


# ------------------------------------------------------------------ Google
class GoogleEmbedder:
    def __init__(self, settings: Settings):
        from google import genai
        from google.genai import types

        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env or set EMBED_PROVIDER=euri.")
        self._types = types
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self.model, self.dim = settings.embed_model, settings.embed_dim

    @_retry
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        t = self._types
        contents = [t.Content(parts=[t.Part(text=x)]) for x in texts]  # one Content per chunk -> one vector each
        result = self._client.models.embed_content(
            model=self.model, contents=contents,
            config=t.EmbedContentConfig(output_dimensionality=self.dim),
        )
        vectors = [e.values for e in result.embeddings]
        if len(vectors) != len(texts):
            raise RuntimeError(f"expected {len(texts)} embeddings, got {len(vectors)}")
        return vectors


# -------------------------------------------------------------------- EURI
class EuriEmbedder:
    """Euron EURI gateway (OpenAI-compatible). Check the model name in your EURI dashboard."""

    def __init__(self, settings: Settings):
        from openai import OpenAI

        if not settings.euri_api_key:
            raise RuntimeError("EURI_API_KEY is not set. Add it to .env or set EMBED_PROVIDER=google.")
        self._client = OpenAI(api_key=settings.euri_api_key, base_url=settings.euri_base_url)
        self.model, self.dim = settings.embed_model, settings.embed_dim

    @_retry
    def _call(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(model=self.model, input=texts, dimensions=self.dim)
        return [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self._call(texts)
        if len(vectors) != len(texts):  # gateway aggregated the batch: fall back to one call per text
            vectors = [self._call([x])[0] for x in texts]
        return vectors


# -------------------------------------------------------------------- fake
class FakeEmbedder:
    """Deterministic hashed bag-of-words. Lets the pipeline run with no API key. Not for submission."""

    def __init__(self, settings: Settings):
        self.model, self.dim = "fake-hash-embedder", settings.embed_dim

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        out = []
        for text in texts:
            body = text.split("|", 1)[-1].lower()
            v = [0.0] * self.dim
            for tok in re.findall(r"[a-z0-9]+", body):
                if len(tok) < 3:
                    continue
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                v[h % self.dim] += 1.0 if (h >> 64) & 1 else -1.0
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


def get_embedder(settings: Settings) -> Embedder:
    providers = {"google": GoogleEmbedder, "euri": EuriEmbedder, "fake": FakeEmbedder}
    if settings.provider not in providers:
        raise ValueError(f"EMBED_PROVIDER must be one of {list(providers)}, got {settings.provider!r}")
    return providers[settings.provider](settings)


# ------------------------------------------------------------------- cache
class EmbeddingCache:
    """JSONL cache so re-running ingest does not re-pay for (or re-wait on) the same chunks."""

    def __init__(self, cache_dir: Path, model: str, dim: int):
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.path = cache_dir / f"embeddings-{model.replace('/', '_')}-{dim}.jsonl"
        self.model, self.dim = model, dim
        self._data: dict[str, list[float]] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                self._data[rec["key"]] = rec["vector"]

    def key(self, text: str) -> str:
        return hashlib.sha256(f"{self.model}|{self.dim}|{text}".encode()).hexdigest()

    def get(self, text: str) -> list[float] | None:
        return self._data.get(self.key(text))

    def put_many(self, texts: list[str], vectors: list[list[float]]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            for t, v in zip(texts, vectors):
                k = self.key(t)
                self._data[k] = v
                f.write(json.dumps({"key": k, "vector": v}) + "\n")


def embed_texts(embedder: Embedder, texts: list[str], cache: EmbeddingCache | None,
                batch_size: int = 16, pause_s: float = 0.0, progress=None) -> list[list[float]]:
    """Embed texts in batches, using and filling the cache. Validates vector size."""
    vectors: list[list[float] | None] = [cache.get(t) if cache else None for t in texts]
    todo = [i for i, v in enumerate(vectors) if v is None]
    for start in range(0, len(todo), batch_size):
        idx = todo[start:start + batch_size]
        batch = [texts[i] for i in idx]
        result = embedder.embed_batch(batch)
        for i, v in zip(idx, result):
            if len(v) != embedder.dim:
                raise RuntimeError(f"embedding has {len(v)} dimensions, expected {embedder.dim}")
            vectors[i] = v
        if cache:
            cache.put_many(batch, result)
        if progress:
            progress(len(idx))
        if pause_s and start + batch_size < len(todo):
            time.sleep(pause_s)
    return vectors  # type: ignore[return-value]
