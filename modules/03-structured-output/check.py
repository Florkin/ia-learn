from course.harness import Check

check = Check(__file__, reference="assistant.llm")
ex = check.exercise

with check.step("QuestionAnalysis déclare le champ search_query"):
    fields = ex.QuestionAnalysis.model_fields
    assert "search_query" in fields, f"champs déclarés : {list(fields)}. Ajoute `search_query: str`."
    assert fields["search_query"].annotation is str, "search_query doit être de type str"

with check.step("analyze_question renvoie un objet QuestionAnalysis validé"):
    analysis = ex.analyze_question("Comment définir une route avec un paramètre optionnel ?")
    assert isinstance(analysis, ex.QuestionAnalysis), (
        f"un objet QuestionAnalysis est attendu, obtenu : {type(analysis).__name__}. "
        "Valide le JSON du modèle avec QuestionAnalysis.model_validate_json(...)."
    )
    assert analysis.language == "fr", f"langue attendue : fr, obtenu : {analysis.language}"
    assert analysis.about_laravel is True, "une question sur les routes concerne Laravel"
    assert "route" in analysis.search_query.lower(), (
        f"la requête de recherche devait parler de « route », obtenu : {analysis.search_query!r}"
    )

with check.step("une question hors sujet en anglais est reconnue comme telle"):
    analysis = ex.analyze_question("What's the best pizza topping?")
    assert analysis.language == "en", f"langue attendue : en, obtenu : {analysis.language}"
    assert analysis.about_laravel is False, "une question sur les pizzas ne concerne pas Laravel"

check.finish()
