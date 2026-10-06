# 06 · Pour aller plus loin

Exercices facultatifs, sans check.

## Filtres composés

Chroma accepte des opérateurs dans `where` : `{"section": {"$in": ["Database", "Eloquent ORM"]}}`,
`{"$and": [...]}`, `{"source": {"$ne": "upgrade.md"}}`. Écris une recherche limitée aux sections qui parlent
de données, puis une recherche qui exclut une page.

## Supprimer et réindexer une page

Écris `reindex_page(source, collection)` qui supprime tous les passages d'une page
(`collection.delete(where={"source": source})`) puis réindexe sa version actuelle. C'est nécessaire dès
qu'une page raccourcit : `upsert` remplace les passages existants mais laisse en place ceux qui n'existent
plus.

## Les mêmes notions avec pgvector

Si tu as Docker, lance PostgreSQL avec l'extension (`docker run -e POSTGRES_PASSWORD=dev -p 5432:5432
pgvector/pgvector:pg17`). Crée une table `chunks (id text primary key, source text, section text, heading
text, body text, embedding vector(1024))`, insère l'échantillon, puis cherche avec
`ORDER BY embedding <=> $1 LIMIT 5`. L'opérateur `<=>` est la distance cosinus. Le filtre devient un `WHERE`
ordinaire, et tu peux joindre tes tables métier.

## Comparer les distances et les similarités

Ajoute `include=["distances"]` à la requête et vérifie, sur quelques passages, que `1 - distance` redonne la
similarité cosinus calculée à la main au module 4.
