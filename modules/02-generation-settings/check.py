from collections.abc import Iterator

from course.harness import Check

check = Check(__file__, reference="assistant.llm")
ex = check.exercise

NAME_PROMPT = "Invent a name for a coffee shop. Reply with the name only."

with check.step("stream_answer est un générateur qui produit la réponse par morceaux"):
    stream = ex.stream_answer("Count from 1 to 10, one number per line.")
    assert isinstance(stream, Iterator) and not isinstance(stream, (str, list)), (
        f"un générateur est attendu (mot-clé `yield`), obtenu : {type(stream).__name__}"
    )
    pieces = list(stream)
    assert len(pieces) >= 2, f"plusieurs morceaux sont attendus, obtenu : {len(pieces)}"
    assert all(isinstance(piece, str) and piece for piece in pieces), (
        "chaque morceau doit être une chaîne non vide (certains événements du flux n'ont pas de texte, il faut les ignorer)"
    )
    assert "10" in "".join(pieces), f"la réponse assemblée devait compter jusqu'à 10, obtenu : {''.join(pieces)!r}"

with check.step("variants à température 0 donne toujours la même réponse"):
    answers = ex.variants(NAME_PROMPT, temperature=0, n=3)
    assert isinstance(answers, list) and len(answers) == 3, f"une liste de 3 réponses est attendue, obtenu : {answers!r}"
    assert len(set(answers)) == 1, f"à température 0 les réponses devaient être identiques, obtenu : {answers}"

with check.step("variants à température 1.5 donne des réponses différentes"):
    answers = ex.variants(NAME_PROMPT, temperature=1.5, n=6)
    assert len(set(answers)) >= 2, (
        f"à température 1.5 au moins deux réponses différentes étaient attendues, obtenu : {answers}. "
        "Vérifie que `temperature` est bien transmis au modèle."
    )

check.finish()
