"""Retrieval strategies over the reference index: vector, keyword (BM25) and hybrid. Reference brick for module 09."""

import math
import re
from collections import Counter, defaultdict
from functools import lru_cache

from assistant.chunking import Chunk, chunk_corpus
from assistant.llm import analyze_question
from assistant.store import query_index, reference_index

# Identifiers stay whole: "whereBelongsTo" and "APP_DEBUG" are single tokens.
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN.findall(text)]


class BM25:
    """Keyword search. A document scores high when it contains the query's rare words, often, in few words."""

    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        counts = [Counter(tokenize(text)) for text in texts]
        self.lengths = [sum(count.values()) for count in counts]
        self.average_length = sum(self.lengths) / len(texts)
        # term -> [(document index, occurrences)]
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for index, count in enumerate(counts):
            for term, occurrences in count.items():
                self.postings[term].append((index, occurrences))
        self.idf = {
            term: math.log(1 + (len(texts) - len(docs) + 0.5) / (len(docs) + 0.5)) for term, docs in self.postings.items()
        }

    def search(self, query: str, k: int) -> list[int]:
        scores: dict[int, float] = defaultdict(float)
        for term in set(tokenize(query)):
            for index, occurrences in self.postings.get(term, ()):
                length_penalty = 1 - self.b + self.b * self.lengths[index] / self.average_length
                scores[index] += self.idf[term] * occurrences * (self.k1 + 1) / (occurrences + self.k1 * length_penalty)
        return sorted(scores, key=scores.get, reverse=True)[:k]


@lru_cache
def _corpus() -> tuple[list[Chunk], dict[str, Chunk], BM25]:
    chunks = chunk_corpus()
    return chunks, {chunk.id: chunk for chunk in chunks}, BM25([chunk.content for chunk in chunks])


def vector_search(question: str, k: int = 5) -> list[Chunk]:
    return query_index(question, reference_index(), k)


def keyword_search(query: str, k: int = 5) -> list[Chunk]:
    chunks, _, bm25 = _corpus()
    return [chunks[index] for index in bm25.search(query, k)]


# --- Module 09: hybrid search --------------------------------------------------------------


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Merges several rankings of ids. An id earns 1 / (k + rank) in each ranking where it appears."""
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, id in enumerate(ranking, start=1):
            scores[id] += 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


def hybrid_search(question: str, k: int = 5, depth: int = 20) -> list[Chunk]:
    """Vector search on the question, keyword search on its English rewrite, merged by rank."""
    _, by_id, _ = _corpus()
    by_meaning = [chunk.id for chunk in vector_search(question, depth)]
    by_keywords = [chunk.id for chunk in keyword_search(analyze_question(question).search_query, depth)]
    return [by_id[id] for id in reciprocal_rank_fusion([by_meaning, by_keywords])[:k]]
