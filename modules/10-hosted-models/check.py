import dataclasses

from assistant import hosted
from assistant.config import settings
from course.harness import Check

check = Check(__file__, reference="assistant.hosted")
ex = check.exercise

MESSAGES = [{"role": "user", "content": "Reply with the single word: pong"}]

with check.step("cost convertit des tokens en dollars à partir de prix au million"):
    cases = [((1_000, 500, 2.0, 10.0), 0.007), ((1_950, 60, 0.10, 0.50), 0.000225), ((5_000, 5_000, 0.0, 0.0), 0.0)]
    for arguments, expected in cases:
        result = ex.cost(*arguments)
        assert result is not None and abs(result - expected) < 1e-12, (
            f"cost{arguments} devait valoir {expected}, obtenu : {result!r}. "
            "Les prix sont en dollars par million de tokens, entrée et sortie séparées."
        )

with check.step("ask_target interroge une cible et rapporte durée, tokens et coût"):
    local = hosted.local_target()
    run = ex.ask_target(local, MESSAGES)
    assert isinstance(run, hosted.Run), f"un objet Run est attendu, obtenu : {type(run).__name__}"
    assert run.target == local.name, f"Run.target doit reprendre le nom de la cible, obtenu : {run.target!r}"
    assert "pong" in run.answer.lower(), f"réponse obtenue : {run.answer!r}"
    assert run.seconds > 0, "Run.seconds doit mesurer la durée de l'appel"
    assert run.prompt_tokens > 0 and run.completion_tokens > 0, "les tokens se lisent dans response.usage"
    assert run.cost == 0, f"un modèle local a un prix de 0, coût obtenu : {run.cost}"

with check.step("le coût d'un appel vient des tokens consommés et des prix de la cible"):
    priced = dataclasses.replace(hosted.local_target(), name="priced", price_in=3.0, price_out=15.0)
    run = ex.ask_target(priced, MESSAGES)
    expected = (run.prompt_tokens * 3.0 + run.completion_tokens * 15.0) / 1_000_000
    assert abs(run.cost - expected) < 1e-12, f"coût attendu : {expected}, obtenu : {run.cost}"

with check.step("compare pose la même question, avec les mêmes passages, à chaque cible"):
    targets = [hosted.local_target(), priced]
    runs = ex.compare("Avec le Laravel AI SDK, quelle commande Artisan crée un agent ?", targets)
    assert isinstance(runs, list) and [run.target for run in runs] == [t.name for t in targets], (
        "compare doit renvoyer un Run par cible, dans l'ordre des cibles"
    )
    assert all("make:agent" in run.answer for run in runs), "chaque réponse devait s'appuyer sur les passages retrouvés"
    assert runs[0].prompt_tokens == runs[1].prompt_tokens, "les cibles doivent recevoir exactement le même prompt"

if settings.openrouter_api_key:
    with check.step("les modèles hébergés de HOSTED_MODELS répondent via OpenRouter"):
        runs = ex.compare("Comment hacher un mot de passe ?", hosted.hosted_targets())
        for run in runs:
            assert run.answer.strip(), f"{run.target} n'a rien répondu"
            print(f"       {run.target:36s} {run.seconds:5.1f} s  {run.prompt_tokens} + {run.completion_tokens} tokens  {run.cost:.6f} $")
else:
    print("  [--] Clé OpenRouter absente : la comparaison avec des modèles hébergés n'a pas été lancée.")
    print("       Renseigne OPENROUTER_API_KEY dans .env puis relance ce check pour la vérifier.")

check.finish()
