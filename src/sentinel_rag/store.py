"""Qdrant helpers: connect, create the collection, upsert, search."""

from __future__ import annotations

import uuid
import warnings

from qdrant_client import QdrantClient, models

from .chunking import Chunk
from .config import Settings

# Fixed namespace so the same chunk always gets the same point ID (re-runs overwrite, never duplicate).
_NAMESPACE = uuid.UUID("5e7f1a2c-0b8d-4d3e-9a61-5e1f7c2b9d40")


def get_client(settings: Settings) -> QdrantClient:
    if not settings.qdrant_url:
        raise RuntimeError("QDRANT_URL is not set. Copy .env.example to .env and fill it in.")
    if settings.qdrant_url == ":memory:":  # in-process, for tests
        return QdrantClient(location=":memory:")
    if settings.qdrant_url.startswith("local:"):
        warnings.filterwarnings("ignore", message="Payload indexes have no effect")  # on-disk local mode for offline dry runs, e.g. local:./qdrant_local
        return QdrantClient(path=settings.qdrant_url.removeprefix("local:"))
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=60)


def point_id(chunk: Chunk) -> str:
    return str(uuid.uuid5(_NAMESPACE, chunk.chunk_id))


def ensure_collection(client: QdrantClient, name: str, dim: int, recreate: bool = False) -> None:
    """Cosine distance: Gemini embeddings are compared by direction, and Google recommends cosine."""
    if client.collection_exists(name):
        if not recreate:
            info = client.get_collection(name)
            size = info.config.params.vectors.size
            if size != dim:
                raise RuntimeError(f"collection {name!r} has size {size}, expected {dim}; run with --recreate")
            return
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
    )
    # Payload indexes make filtered search fast (and Qdrant Cloud strict mode requires them for filters).
    for field, schema in [("doc_type", models.PayloadSchemaType.KEYWORD),
                          ("source_document", models.PayloadSchemaType.KEYWORD),
                          ("chunk_number", models.PayloadSchemaType.INTEGER)]:
        client.create_payload_index(name, field_name=field, field_schema=schema)


def upsert_chunks(client: QdrantClient, name: str, chunks: list[Chunk], vectors: list[list[float]],
                  batch_size: int = 64, progress=None) -> None:
    for start in range(0, len(chunks), batch_size):
        part = list(zip(chunks[start:start + batch_size], vectors[start:start + batch_size]))
        points = [
            models.PointStruct(
                id=point_id(c), vector=v,
                payload={
                    "source_document": c.source_document,
                    "doc_type": c.doc_type,
                    "chunk_number": c.chunk_number,
                    "total_chunks": c.total_chunks,
                    "title": c.title,
                    "text": c.text,
                },
            )
            for c, v in part
        ]
        client.upsert(collection_name=name, points=points, wait=True)
        if progress:
            progress(len(points))


def search(client: QdrantClient, name: str, vector: list[float], limit: int = 5,
           doc_type: str | None = None) -> list[models.ScoredPoint]:
    query_filter = None
    if doc_type:
        query_filter = models.Filter(must=[models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type))])
    return client.query_points(collection_name=name, query=vector, limit=limit,
                               query_filter=query_filter, with_payload=True).points
