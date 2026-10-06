import re

from assistant import rag
from assistant.chunking import Chunk
from course.harness import Check

check = Check(__file__, reference="assistant.rag")
ex = check.exercise

PASSAGES = [
    Chunk("cache.md#3", "cache.md", "Digging Deeper", "Cache > Storing Items", "Use the put method to store an item."),
    Chunk("routing.md#7", "routing.md", "The Basics", "Routing > Named Routes", "Named routes allow URL generation."),
]

with check.step("build_prompt numérote les passages et termine par la question"):
    messages = ex.build_prompt("How do I name a route?", PASSAGES)
    assert isinstance(messages, list) and len(messages) == 2, f"deux messages attendus (system puis user), obtenu : {messages!r}"
    assert messages[0]["role"] == "system" and messages[0]["content"].strip(), "le premier message doit porter les consignes (rôle system)"
    user = messages[1]["content"]
    assert messages[1]["role"] == "user", "le second message doit avoir le rôle user"
    for number, passage in enumerate(PASSAGES, start=1):
        assert f"[{number}]" in user, f"le passage {number} doit être précédé de son numéro entre crochets : [{number}]"
        assert passage.text in user, f"le texte du passage {number} est absent du prompt"
        assert passage.source in user, f"la source du passage {number} ({passage.source}) est absente du prompt"
    assert user.index("[1]") < user.index("[2]") < user.index("How do I name a route?"), (
        "ordre attendu : passage [1], passage [2], puis la question"
    )

with check.step("answer renvoie la réponse et les passages utilisés"):
    result = ex.answer("Comment stocker une valeur dans le cache sans date d'expiration ?", k=4)
    assert isinstance(result, rag.Answer), f"un objet Answer est attendu, obtenu : {type(result).__name__}"
    assert isinstance(result.text, str) and result.text.strip(), "le texte de la réponse est vide"
    assert len(result.sources) == 4 and all(isinstance(c, Chunk) for c in result.sources), "4 passages attendus dans sources (k=4)"
    assert "cache.md" in {c.source for c in result.sources}, f"cache.md devait figurer parmi les sources, obtenu : {[c.source for c in result.sources]}"

with check.step("la réponse cite ses passages et s'appuie sur la documentation"):
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", result.text)}
    assert cited and cited <= {1, 2, 3, 4}, f"la réponse doit citer au moins un passage entre [1] et [4], obtenu : {result.text!r}"
    assert "forever" in result.text, f"la réponse devait mentionner la méthode `forever`, obtenu : {result.text!r}"

with check.step("la question témoin du module 2 reçoit maintenant la bonne réponse"):
    result = ex.answer("Avec le Laravel AI SDK, quelle commande Artisan crée un agent ?")
    assert "make:agent" in result.text, f"la réponse devait contenir `make:agent`, obtenu : {result.text!r}"

check.finish()
