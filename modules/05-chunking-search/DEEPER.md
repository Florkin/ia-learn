# 05 · Pour aller plus loin

Exercices facultatifs, sans check.

## Découper à taille fixe avec recouvrement

Écris `chunk_fixed(text, size=150, overlap=30)` qui coupe tous les `size` mots en reprenant les `overlap`
derniers mots du passage précédent. Le recouvrement évite qu'une phrase coupée en deux soit introuvable.
Cherche la même question avec les deux découpages et compare les passages remontés.

## Lire ce que tu indexes

Affiche les vingt passages les plus courts et les vingt plus longs du corpus complet
(`chunk_corpus()` dans `assistant/chunking.py`). Repère ceux qui n'apportent rien et ceux qui mélangent
plusieurs sujets. C'est la revue la plus rentable qu'on puisse faire sur un RAG, et presque personne ne la
fait.

## Avec ou sans le chemin des titres

Calcule les vecteurs de l'échantillon à partir de `chunk.text` au lieu de `chunk.content`, et compare les
résultats sur des questions où le sujet n'apparaît que dans le titre (« How do I exclude a middleware? »).

## Changer la taille maximale

Découpe avec `max_words=80` puis `max_words=600`. Compte les passages, puis observe sur trois questions si le
bon passage remonte plus haut ou plus bas. Garde tes observations pour le module 8, où tu pourras remplacer
l'impression par un chiffre.
