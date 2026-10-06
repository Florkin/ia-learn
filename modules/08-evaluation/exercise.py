"""Module 08: evaluation. Read LESSON.md first.

Run this file to measure the assistant's retrieval on the reference questions.
"""

from collections.abc import Callable

from assistant.chunking import Chunk
from assistant.evaluation import is_relevant, load_golden
from assistant.retrieval import vector_search


def first_relevant_rank(chunks: list[Chunk], case: dict) -> int | None:
    """Rank (starting at 1) of the first chunk for which is_relevant(chunk, case) is true, or None."""
    raise NotImplementedError


def hit_rate(ranks: list[int | None], k: int = 5) -> float:
    """Share of questions whose first relevant chunk is ranked k or better. None counts as a miss."""
    raise NotImplementedError


def mrr(ranks: list[int | None]) -> float:
    """Mean reciprocal rank: the average of 1 / rank over all questions, a miss counting for 0."""
    raise NotImplementedError


def evaluate(retriever: Callable[[str], list[Chunk]], golden: list[dict], k: int = 5) -> dict:
    """Runs the retriever on every question and returns the measures.

    retriever(question) returns ranked chunks. Only the first k count.
    Returned dict:
      "hit_rate"  hit_rate of the ranks at k
      "mrr"       mrr of the ranks
      "ranks"     one rank (or None) per question, in the order of `golden`
      "misses"    the questions with no relevant chunk in the first k
    """
    raise NotImplementedError


if __name__ == "__main__":
    golden = load_golden()
    report = evaluate(vector_search, golden, k=5)
    print(f"{len(golden)} questions")
    print(f"hit rate à 5 : {report['hit_rate']:.3f}")
    print(f"MRR          : {report['mrr']:.3f}")
    print("\nQuestions sans passage pertinent dans les 5 premiers :")
    for question in report["misses"]:
        print(f"\n  {question}")
        for chunk in vector_search(question, 5):
            print(f"      {chunk.source:24s} {chunk.heading}")
