"""Measuring retrieval against a set of reference questions: reference brick for module 08."""

import json
from collections.abc import Callable

from assistant.chunking import Chunk
from assistant.config import ROOT

GOLDEN_PATH = ROOT / "data" / "golden.jsonl"


def load_golden() -> list[dict]:
    """One case per line: {"question": ..., "sources": [pages], "contains": [terms]}."""
    lines = GOLDEN_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def is_relevant(chunk: Chunk, case: dict) -> bool:
    """A passage answers a case when it comes from an expected page and contains one of the expected terms."""
    content = chunk.content.lower()
    return chunk.source in case["sources"] and any(term.lower() in content for term in case["contains"])


# --- Module 08: evaluation ---------------------------------------------------------------


def first_relevant_rank(chunks: list[Chunk], case: dict) -> int | None:
    for rank, chunk in enumerate(chunks, start=1):
        if is_relevant(chunk, case):
            return rank
    return None


def hit_rate(ranks: list[int | None], k: int = 5) -> float:
    return sum(rank is not None and rank <= k for rank in ranks) / len(ranks)


def mrr(ranks: list[int | None]) -> float:
    return sum(1 / rank for rank in ranks if rank) / len(ranks)


def evaluate(retriever: Callable[[str], list[Chunk]], golden: list[dict], k: int = 5) -> dict:
    ranks = [first_relevant_rank(retriever(case["question"])[:k], case) for case in golden]
    return {
        "hit_rate": hit_rate(ranks, k),
        "mrr": mrr(ranks),
        "ranks": ranks,
        "misses": [case["question"] for case, rank in zip(golden, ranks) if rank is None],
    }
