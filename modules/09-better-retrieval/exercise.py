"""Module 09: better retrieval. Read LESSON.md first.

Run this file to compare five retrieval strategies on the reference questions (about one minute).
"""

from assistant.chunking import Chunk
from assistant.evaluation import evaluate, load_golden
from assistant.llm import analyze_question
from assistant.retrieval import keyword_search, vector_search


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Merges several rankings of ids into one, best first.

    Every id earns 1 / (k + rank) in each ranking where it appears, rank starting at 1.
    The scores of an id add up across rankings. Each id appears once in the result.
    """
    raise NotImplementedError


def hybrid_search(question: str, k: int = 5, depth: int = 20, rewrite: bool = True) -> list[Chunk]:
    """Combines a search by meaning and a search by keywords.

    1. vector_search(question, depth) gives the `depth` closest chunks by meaning.
    2. keyword_search(query, depth) gives the `depth` best chunks by keywords. The query is the English
       rewrite of the question, analyze_question(question).search_query, or the question itself when
       `rewrite` is False.
    3. Merge the two lists of chunk ids with reciprocal_rank_fusion and keep the first k.
    4. Return the Chunk objects, in the merged order.
    """
    raise NotImplementedError


if __name__ == "__main__":
    golden = load_golden()
    strategies = {
        "vectorielle": vector_search,
        "mots-clés, question brute": keyword_search,
        "mots-clés, question réécrite": lambda q, k=5: keyword_search(analyze_question(q).search_query, k),
        "hybride, question brute": lambda q, k=5: hybrid_search(q, k, rewrite=False),
        "hybride, question réécrite": hybrid_search,
    }
    print(f"{'stratégie':30s} hit@1  hit@5  MRR")
    for name, retriever in strategies.items():
        report = evaluate(retriever, golden, k=5)
        first = sum(rank == 1 for rank in report["ranks"]) / len(golden)
        print(f"{name:30s} {first:.3f}  {report['hit_rate']:.3f}  {report['mrr']:.3f}")
