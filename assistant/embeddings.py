"""Turning text into vectors and comparing them: reference brick for module 04."""

from functools import lru_cache

import numpy as np
from openai import OpenAI

from assistant.config import settings


@lru_cache
def client() -> OpenAI:
    return OpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)


def embed(texts: list[str], batch_size: int = 64) -> np.ndarray:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        response = client().embeddings.create(model=settings.embed_model, input=texts[start : start + batch_size])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def rank(query: str, candidates: list[str]) -> list[tuple[str, float]]:
    query_vector, *candidate_vectors = embed([query, *candidates])
    scored = [(text, cosine_similarity(query_vector, vector)) for text, vector in zip(candidates, candidate_vectors)]
    return sorted(scored, key=lambda pair: pair[1], reverse=True)
