"""Module 04: embeddings. Read LESSON.md first.

Run this file to see which sentences the embedding model considers close to each other.
"""

import numpy as np
from openai import OpenAI

from assistant.config import settings

client = OpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)


def embed(texts: list[str]) -> np.ndarray:
    """Returns one vector per text, as an array of shape (len(texts), dimensions).

    Call client.embeddings.create(model=settings.embed_model, input=texts).
    The vector of the i-th text is response.data[i].embedding (a list of floats).
    """
    raise NotImplementedError


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine of the angle between two vectors: dot product divided by the product of the norms.

    Write it with np.dot and np.linalg.norm.
    """
    raise NotImplementedError


def rank(query: str, candidates: list[str]) -> list[tuple[str, float]]:
    """Returns (candidate, similarity to the query) pairs, most similar first."""
    raise NotImplementedError


if __name__ == "__main__":
    candidates = [
        "Rate limiters restrict how many requests a client may send in a given amount of time.",
        "You may limit the number of results returned from a query using the limit method.",
        "The Hash facade provides secure Bcrypt and Argon2 hashing for storing user passwords.",
        "Les limiteurs de débit plafonnent le nombre de requêtes qu'un client peut envoyer.",
        "Blade is the templating engine included with Laravel.",
    ]
    queries = (
        "How do I limit the number of requests per minute?",
        "Comment stocker un mot de passe de façon sûre ?",
        "How do I throttle an API?",
    )
    for query in queries:
        print(f"\n> {query}")
        for text, score in rank(query, candidates):
            print(f"  {score:.3f}  {text}")
