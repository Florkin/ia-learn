# 04 · Pour aller plus loin

Exercices facultatifs, sans check.

## Comparer d'un coup avec un produit de matrices

`bge-m3` renvoie des vecteurs de longueur 1, ce que tu peux vérifier avec `np.linalg.norm(vectors, axis=1)`.
Pour de tels vecteurs, le cosinus se réduit au produit scalaire, et `vectors @ vectors.T` donne toutes les
similarités en une opération. Affiche cette matrice pour six phrases et retrouve les paires proches.

## Un modèle qui ne parle qu'anglais

Télécharge `nomic-embed-text` (`ollama pull nomic-embed-text`), mets `EMBED_MODEL=nomic-embed-text` dans ton
`.env` et relance ta copie. Regarde ce que devient le classement de la question en français. Remets ensuite
`bge-m3`.

## Chercher le point de rupture

Écris dix paires de phrases : paraphrases, contraires (« activer le cache » et « désactiver le cache »),
même sujet avec un détail qui change (« 60 requêtes par minute » et « 600 requêtes par minute »). Note les
scores. Les embeddings distinguent mal une négation ou un nombre, ce qui est une limite à connaître avant de
leur confier une recherche précise.

## Voir l'espace

Avec `numpy.linalg.svd`, projette en deux dimensions les vecteurs d'une
trentaine de titres de la documentation et trace-les. Les pages d'un même thème se regroupent.
