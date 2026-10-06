"""A persistent vector index with Chroma: reference brick for module 06."""

import re
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from assistant.chunking import Chunk, chunk_corpus
from assistant.config import DATA_DIR, settings
from assistant.embeddings import embed


def open_collection(path: Path, name: str = "docs") -> Collection:
    """Opens (or creates) a collection stored on disk. We provide our own vectors, compared by cosine."""
    client = chromadb.PersistentClient(path=str(path))
    return client.get_or_create_collection(name, embedding_function=None, configuration={"hnsw": {"space": "cosine"}})


def build_index(chunks: list[Chunk], collection: Collection, batch_size: int = 256) -> int:
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        collection.upsert(
            ids=[chunk.id for chunk in batch],
            embeddings=embed([chunk.content for chunk in batch]),
            documents=[chunk.text for chunk in batch],
            metadatas=[{"source": c.source, "section": c.section, "heading": c.heading} for c in batch],
        )
    return collection.count()


def query_index(question: str, collection: Collection, k: int = 5, where: dict | None = None) -> list[Chunk]:
    result = collection.query(query_embeddings=embed([question]), n_results=k, where=where)
    return [
        Chunk(id, meta["source"], meta["section"], meta["heading"], text)
        for id, text, meta in zip(result["ids"][0], result["documents"][0], result["metadatas"][0])
    ]


@lru_cache
def reference_index() -> Collection:
    """The index of the whole corpus used from module 07 on. Built on first use, one folder per embedding model."""
    model = re.sub(r"[^\w.-]", "_", settings.embed_model)
    collection = open_collection(DATA_DIR / f"reference-{model}")
    if collection.count() == 0:
        chunks = chunk_corpus()
        print(f"Construction de l'index complet : {len(chunks)} passages, compte une à deux minutes sur un Mac récent...")
        build_index(chunks, collection)
    return collection


if __name__ == "__main__":
    print(f"{reference_index().count()} passages dans l'index de référence")
