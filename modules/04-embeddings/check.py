import numpy as np

from course.harness import Check

check = Check(__file__, reference="assistant.embeddings")
ex = check.exercise

SENTENCES = [
    "Rate limiters restrict how many requests a client may send in a given amount of time.",
    "Eloquent relationships are defined as methods on your model classes.",
    "Blade is the templating engine included with Laravel.",
    "The Hash facade provides secure Bcrypt and Argon2 hashing for storing user passwords.",
]

with check.step("cosine_similarity calcule le cosinus de l'angle entre deux vecteurs"):
    cases = [([1, 0], [0, 1], 0.0), ([1, 2, 3], [2, 4, 6], 1.0), ([1, 0], [-1, 0], -1.0), ([3, 4], [4, 3], 0.96)]
    for a, b, expected in cases:
        result = ex.cosine_similarity(np.array(a, dtype=float), np.array(b, dtype=float))
        assert result is not None, "la fonction ne renvoie rien"
        assert abs(float(result) - expected) < 1e-6, (
            f"cosine_similarity({a}, {b}) devait valoir {expected}, obtenu : {float(result):.4f}. "
            "Formule : produit scalaire divisé par le produit des normes."
        )

with check.step("embed renvoie une matrice, une ligne par texte"):
    vectors = ex.embed(SENTENCES[:3])
    assert isinstance(vectors, np.ndarray), f"un tableau numpy est attendu, obtenu : {type(vectors).__name__}"
    assert vectors.ndim == 2 and vectors.shape[0] == 3, f"forme attendue : (3, dimensions), obtenu : {vectors.shape}"
    assert vectors.shape[1] >= 100, f"un embedding a des centaines de dimensions, obtenu : {vectors.shape[1]}"

with check.step("rank classe les candidats du plus proche au plus éloigné"):
    ranked = ex.rank("How do I limit the number of requests per minute?", SENTENCES)
    assert isinstance(ranked, list) and len(ranked) == len(SENTENCES), "une liste de (texte, score) par candidat est attendue"
    scores = [score for _, score in ranked]
    assert scores == sorted(scores, reverse=True), f"les scores doivent être décroissants, obtenu : {[round(s, 3) for s in scores]}"
    assert ranked[0][0] == SENTENCES[0], f"le premier résultat devait parler de rate limiting, obtenu : {ranked[0][0]!r}"

with check.step("une question en français retrouve un passage en anglais"):
    ranked = ex.rank("Comment stocker un mot de passe de façon sûre ?", SENTENCES)
    assert ranked[0][0] == SENTENCES[3], f"le premier résultat devait parler de hachage, obtenu : {ranked[0][0]!r}"

check.finish()
