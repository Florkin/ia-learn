from assistant import evaluation, retrieval
from assistant.chunking import Chunk
from course.harness import Check

check = Check(__file__, reference="assistant.evaluation")
ex = check.exercise


def chunk(source: str, text: str) -> Chunk:
    return Chunk(f"{source}#0", source, "", source, text)


CASE = {"question": "How do I cache forever?", "sources": ["cache.md"], "contains": ["forever"]}
RESULTS = [chunk("queues.md", "forever"), chunk("cache.md", "put"), chunk("cache.md", "Cache::forever")]

with check.step("first_relevant_rank donne le rang du premier passage pertinent"):
    assert ex.first_relevant_rank(RESULTS, CASE) == 3, (
        f"rang attendu : 3 (le premier passage vient d'une autre page, le deuxième ne contient pas le terme), "
        f"obtenu : {ex.first_relevant_rank(RESULTS, CASE)!r}. Les rangs commencent à 1."
    )
    assert ex.first_relevant_rank(RESULTS[:2], CASE) is None, "sans passage pertinent, le rang doit être None"

with check.step("hit_rate compte les questions dont un passage pertinent est dans les k premiers"):
    ranks = [1, 3, None, 6]
    for k, expected in ((5, 0.5), (1, 0.25), (10, 0.75)):
        result = ex.hit_rate(ranks, k)
        assert result is not None and abs(result - expected) < 1e-9, f"hit_rate({ranks}, k={k}) devait valoir {expected}, obtenu : {result!r}"

with check.step("mrr fait la moyenne des inverses des rangs"):
    result = ex.mrr([1, 2, None, 4])
    assert result is not None and abs(result - 0.4375) < 1e-9, (
        f"mrr([1, 2, None, 4]) devait valoir 0.4375, soit (1 + 1/2 + 0 + 1/4) / 4, obtenu : {result!r}"
    )

with check.step("evaluate applique un retriever à chaque question et rassemble les mesures"):
    golden = [
        CASE,
        {"question": "How do I name a route?", "sources": ["routing.md"], "contains": ["name("]},
        {"question": "How do I hash a password?", "sources": ["hashing.md"], "contains": ["Hash::make"]},
    ]
    fake = {
        golden[0]["question"]: RESULTS,
        golden[1]["question"]: [chunk("routing.md", "->name('profile')")],
        golden[2]["question"]: [chunk("encryption.md", "encrypt"), chunk("cache.md", "put")],
    }
    report = ex.evaluate(lambda question: fake[question], golden, k=5)
    assert isinstance(report, dict) and {"hit_rate", "mrr", "ranks", "misses"} <= set(report), (
        f"un dict avec les clés hit_rate, mrr, ranks et misses est attendu, obtenu : {report!r}"
    )
    assert report["ranks"] == [3, 1, None], f"rangs attendus : [3, 1, None], obtenu : {report['ranks']}"
    assert abs(report["hit_rate"] - 2 / 3) < 1e-9 and abs(report["mrr"] - (1 / 3 + 1) / 3) < 1e-9, (
        f"hit_rate attendu 0.667 et mrr attendu 0.444, obtenu : {report['hit_rate']:.3f} et {report['mrr']:.3f}"
    )
    assert report["misses"] == ["How do I hash a password?"], f"misses doit lister les questions sans passage pertinent, obtenu : {report['misses']}"
    strict = ex.evaluate(lambda question: fake[question], golden, k=2)
    assert strict["ranks"] == [None, 1, None], f"avec k=2 seuls les 2 premiers passages comptent, rangs obtenus : {strict['ranks']}"

with check.step("evaluate mesure la recherche vectorielle de l'assistant sur le jeu de questions"):
    golden = evaluation.load_golden()
    report = ex.evaluate(retrieval.vector_search, golden, k=5)
    expected = evaluation.evaluate(retrieval.vector_search, golden, k=5)
    assert report["ranks"] == expected["ranks"], "les rangs diffèrent de ceux de l'évaluation de référence"
    print(f"       {len(golden)} questions, hit rate {report['hit_rate']:.3f}, MRR {report['mrr']:.3f}, {len(report['misses'])} échecs")

check.finish()
