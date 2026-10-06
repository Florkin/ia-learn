from assistant import chunking, embeddings
from course.harness import Check

check = Check(__file__, reference="assistant.chunking")
ex = check.exercise

PAGE = """# Cache

- [Introduction](#introduction)
- [Usage](#usage)

<a name="introduction"></a>
## Introduction

Caching keeps the result of slow work.

<a name="usage"></a>
## Usage

### Storing items

Use the put method to store an item.

```shell
# Clear the whole cache
php artisan cache:clear
```

### Long section

""" + "\n\n".join(f"Paragraph{i} " + "word " * 19 for i in range(6))

with check.step("chunk_markdown produit un passage par titre, avec le chemin des titres"):
    chunks = ex.chunk_markdown(PAGE, "cache.md", "Digging Deeper", max_words=50)
    assert isinstance(chunks, list) and chunks, "une liste non vide de Chunk est attendue"
    assert all(isinstance(c, chunking.Chunk) for c in chunks), "chaque élément doit être un Chunk"
    assert all(c.source == "cache.md" and c.section == "Digging Deeper" for c in chunks), "source et section doivent être reportées sur chaque passage"
    headings = {c.heading for c in chunks}
    expected = {"Cache > Introduction", "Cache > Usage > Storing items", "Cache > Usage > Long section"}
    assert headings == expected, f"chemins de titres attendus : {sorted(expected)}, obtenu : {sorted(headings)}"

with check.step("une ligne qui commence par # dans un bloc de code n'est pas un titre"):
    storing = [c for c in chunks if c.heading.endswith("Storing items")]
    assert len(storing) == 1 and "# Clear the whole cache" in storing[0].text and "cache:clear" in storing[0].text, (
        "le bloc de code doit rester entier dans le passage « Storing items »"
    )

with check.step("aucun passage vide ni trop long, aucun texte perdu"):
    assert all(c.text.strip() for c in chunks), "un passage est vide"
    sizes = [len(c.text.split()) for c in chunks]
    assert max(sizes) <= 50, f"taille maximale attendue : 50 mots, obtenu : {max(sizes)}"
    long_section = [c for c in chunks if c.heading.endswith("Long section")]
    assert len(long_section) >= 3, f"la section longue (120 mots) devait donner au moins 3 passages, obtenu : {len(long_section)}"
    everything = " ".join(c.text for c in chunks)
    missing = [f"Paragraph{i}" for i in range(6) if everything.count(f"Paragraph{i}") != 1]
    assert not missing, f"paragraphes perdus ou dupliqués : {missing}"
    assert "Caching keeps the result of slow work." in everything, "le texte de l'introduction a disparu"

with check.step("les identifiants suivent la position dans la page"):
    ids = [c.id for c in chunks]
    assert ids == [f"cache.md#{i}" for i in range(len(chunks))], f"identifiants obtenus : {ids}"

with check.step("search renvoie les k passages les plus proches de la question"):
    corpus = chunking.chunk_corpus(sample=True)
    vectors = embeddings.embed([c.content for c in corpus])
    results = ex.search("How do I limit the number of requests per minute?", corpus, vectors, k=3)
    assert isinstance(results, list) and len(results) == 3, f"3 résultats attendus, obtenu : {results!r}"
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True), f"les scores doivent être décroissants, obtenu : {scores}"
    assert results[0][0].source in ("rate-limiting.md", "routing.md"), (
        f"le premier passage devait venir de rate-limiting.md ou routing.md, obtenu : {results[0][0].source} ({results[0][0].heading})"
    )

with check.step("search retrouve un passage en anglais à partir d'une question en français"):
    results = ex.search("Comment hacher un mot de passe ?", corpus, vectors, k=3)
    assert results[0][0].source == "hashing.md", f"le premier passage devait venir de hashing.md, obtenu : {results[0][0].source}"

check.finish()
