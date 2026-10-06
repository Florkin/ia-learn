import dataclasses
import shutil

from assistant import chunking, store
from assistant.config import DATA_DIR
from course.harness import Check

check = Check(__file__, reference="assistant.store")
ex = check.exercise

# A fresh index on every run, separate from the reference index.
index_dir = DATA_DIR / "check-06"
shutil.rmtree(index_dir, ignore_errors=True)
collection = store.open_collection(index_dir)
chunks = chunking.chunk_corpus(sample=True)

with check.step(f"build_index range les {len(chunks)} passages de l'échantillon dans la collection"):
    count = ex.build_index(chunks, collection)
    assert collection.count() == len(chunks), f"{len(chunks)} passages attendus dans la collection, obtenu : {collection.count()}"
    assert count == len(chunks), f"build_index doit renvoyer le nombre de passages de la collection, obtenu : {count!r}"

with check.step("chaque passage est stocké avec son vecteur, son texte et ses métadonnées"):
    first = chunks[0]
    stored = collection.get(ids=[first.id], include=["embeddings", "documents", "metadatas"])
    assert stored["ids"] == [first.id], f"le passage {first.id} est introuvable : les identifiants doivent être ceux des Chunk"
    assert stored["documents"][0] == first.text, "le document stocké doit être `chunk.text`"
    expected = {"source": first.source, "section": first.section, "heading": first.heading}
    assert stored["metadatas"][0] == expected, f"métadonnées attendues : {expected}, obtenu : {stored['metadatas'][0]}"
    assert len(stored["embeddings"][0]) >= 100, "le vecteur stocké doit venir de embed()"

with check.step("réindexer un passage modifié le met à jour, sans doublon"):
    changed = dataclasses.replace(chunks[0], text="This text was updated.")
    ex.build_index([changed], collection)
    assert collection.count() == len(chunks), f"la collection devait garder {len(chunks)} passages, obtenu : {collection.count()}"
    stored = collection.get(ids=[changed.id])["documents"][0]
    assert stored == "This text was updated.", "le texte n'a pas été mis à jour : utilise `upsert`, `add` ignore un identifiant déjà présent"
    ex.build_index([chunks[0]], collection)

with check.step("query_index renvoie les passages les plus proches, sous forme de Chunk"):
    results = ex.query_index("How do I limit the number of requests per minute?", collection, k=3)
    assert isinstance(results, list) and len(results) == 3, f"3 passages attendus, obtenu : {results!r}"
    assert all(isinstance(c, chunking.Chunk) for c in results), "query_index doit reconstruire des objets Chunk"
    assert results[0].source in ("rate-limiting.md", "routing.md"), f"premier passage obtenu : {results[0].source} ({results[0].heading})"
    by_id = {c.id: c for c in chunks}
    assert results[0] == by_id[results[0].id], "le Chunk reconstruit doit être identique à celui qui a été indexé"

with check.step("le filtre where restreint la recherche à une section"):
    results = ex.query_index("How do I create records?", collection, k=4, where={"section": "Database"})
    assert results, "aucun résultat avec le filtre"
    sections = {c.section for c in results}
    assert sections == {"Database"}, f"seule la section Database était attendue, obtenu : {sections}"

check.finish()
