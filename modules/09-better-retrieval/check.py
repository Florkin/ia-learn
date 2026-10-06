from assistant import evaluation, retrieval
from assistant.chunking import Chunk
from course.harness import Check

check = Check(__file__, reference="assistant.retrieval")
ex = check.exercise

with check.step("reciprocal_rank_fusion additionne 1 / (k + rang) pour chaque classement"):
    fused = ex.reciprocal_rank_fusion([["a", "b", "c"], ["b", "c", "d"]], k=60)
    assert fused == ["b", "c", "a", "d"], (
        f"ordre attendu : ['b', 'c', 'a', 'd'], obtenu : {fused!r}. "
        "b vaut 1/62 + 1/61, c vaut 1/63 + 1/62, a vaut 1/61, d vaut 1/63."
    )
    assert ex.reciprocal_rank_fusion([["x", "y"]]) == ["x", "y"], "un classement seul doit ressortir inchangé"
    top_heavy = ex.reciprocal_rank_fusion([["a", "b"], ["c", "a"], ["c", "b"]], k=1)
    assert top_heavy[0] == "c", f"avec k=1, deux premières places battent une première et une deuxième, obtenu : {top_heavy!r}"

with check.step("hybrid_search renvoie k passages distincts"):
    results = ex.hybrid_search("Comment stocker une valeur dans le cache sans date d'expiration ?", k=5)
    assert isinstance(results, list) and len(results) == 5, f"5 passages attendus, obtenu : {results!r}"
    assert all(isinstance(chunk, Chunk) for chunk in results), "hybrid_search doit renvoyer des objets Chunk"
    assert len({chunk.id for chunk in results}) == 5, "un même passage apparaît deux fois : la fusion doit dédoublonner"

with check.step("hybrid_search retrouve l'identifiant exact que la recherche vectorielle manquait"):
    case = {"question": "À quoi sert QUEUE_CONNECTION ?", "sources": ["queues.md"], "contains": ["QUEUE_CONNECTION"]}
    results = ex.hybrid_search(case["question"], k=5)
    assert any(evaluation.is_relevant(chunk, case) for chunk in results), (
        f"aucun passage ne contient QUEUE_CONNECTION, obtenu : {[chunk.heading for chunk in results]}. "
        "La recherche par mots-clés doit participer à la fusion."
    )

with check.step("mesurée sur le jeu de questions, la recherche hybride place le bon passage plus haut"):
    golden = evaluation.load_golden()
    baseline = evaluation.evaluate(retrieval.vector_search, golden, k=5)
    hybrid = evaluation.evaluate(ex.hybrid_search, golden, k=5)
    print(f"       vectorielle : hit rate {baseline['hit_rate']:.3f}, MRR {baseline['mrr']:.3f}")
    print(f"       hybride     : hit rate {hybrid['hit_rate']:.3f}, MRR {hybrid['mrr']:.3f}")
    assert hybrid["mrr"] > baseline["mrr"], (
        "le MRR de la recherche hybride devait dépasser celui de la recherche vectorielle. "
        "Vérifie que les mots-clés sont cherchés avec la requête réécrite en anglais."
    )

check.finish()
