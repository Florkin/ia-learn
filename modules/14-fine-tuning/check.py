import hashlib
import json

from course.harness import Check, require

require("torch", "uv sync --all-groups")

from assistant import finetune
from assistant.chunking import chunk_corpus
from assistant.config import DATA_DIR, settings

check = Check(__file__, reference="assistant.finetune")
ex = check.exercise

chunks = chunk_corpus()

with check.step("build_examples produit un exemple de conversation par passage"):
    examples = ex.build_examples(chunks[:50])
    assert isinstance(examples, list) and len(examples) == 50, "un exemple par passage est attendu"
    for chunk, example in zip(chunks[:50], examples):
        messages = example.get("messages") if isinstance(example, dict) else None
        assert messages and [m["role"] for m in messages] == ["system", "user", "assistant"], (
            f"chaque exemple est un dict {{'messages': [system, user, assistant]}}, obtenu : {example!r:.200}"
        )
        assert messages[0]["content"] == finetune.INSTRUCTION, "le message system doit être INSTRUCTION"
        assert messages[1]["content"] == finetune.excerpt(chunk), "le message user doit être excerpt(chunk)"
        assert messages[2]["content"] == chunk.section, f"la réponse attendue est la section du passage, obtenu : {messages[2]['content']!r}"

with check.step("split_examples sépare entraînement et validation sans recouvrement"):
    items = [{"messages": [{"role": "user", "content": str(n)}]} for n in range(200)]
    train, valid = ex.split_examples(items, valid_ratio=0.1, seed=0)
    assert len(valid) == 20 and len(train) == 180, f"180 et 20 exemples attendus, obtenu : {len(train)} et {len(valid)}"
    keys = lambda group: {item["messages"][0]["content"] for item in group}
    assert not keys(train) & keys(valid), "un même exemple se retrouve dans l'entraînement et dans la validation"
    assert keys(train) | keys(valid) == keys(items), "des exemples ont disparu"
    assert [item["messages"][0]["content"] for item in items] == [str(n) for n in range(200)], "la liste reçue ne doit pas être modifiée"
    assert keys(valid) != {str(n) for n in range(20)} and keys(valid) != {str(n) for n in range(180, 200)}, "les exemples doivent être mélangés avant la coupe"
    again = ex.split_examples(items, valid_ratio=0.1, seed=0)
    assert again == (train, valid), "avec la même graine, le découpage doit être identique"
    assert ex.split_examples(items, valid_ratio=0.1, seed=1)[1] != valid, "une autre graine doit donner un autre découpage"

with check.step(f"le modèle affiné répond bien mieux que le modèle de base (moteur : {settings.finetune_backend})"):
    train, valid = ex.split_examples(ex.build_examples(chunks))
    test = valid[:100]
    before = finetune.accuracy(test)
    # The adapter is kept on disk and reused as long as the training data does not change.
    fingerprint = hashlib.sha1(json.dumps(train, sort_keys=True).encode()).hexdigest()
    adapter = DATA_DIR / f"{check.mode}-{settings.learner or 'course'}-14-{settings.finetune_backend}"
    if not adapter.exists() or (adapter / "dataset.sha1").read_text(encoding="utf-8") != fingerprint:
        print(f"       Entraînement de {settings.finetune_iters} itérations, de 30 secondes à 20 minutes selon la machine...")
        finetune.train(train, valid, adapter)
        (adapter / "dataset.sha1").write_text(fingerprint, encoding="utf-8")
    else:
        print(f"       Adaptateur déjà entraîné sur ces données, réutilisé : {adapter.name}")
    after = finetune.accuracy(test, adapter)
    print(f"       bonnes réponses sur 100 passages de validation : {before:.0%} avant, {after:.0%} après")
    assert after >= 0.75 and after >= before + 0.5, (
        f"une précision d'au moins 75 % après affinage était attendue, obtenu : {after:.0%} (avant : {before:.0%})"
    )

check.finish()
