# 09 · Pour aller plus loin

Exercices facultatifs, sans check. Chacun se termine par une mesure avec `evaluate`.

## Reclasser avec le modèle de conversation

Retrouve vingt passages par recherche vectorielle, puis demande au modèle, avec une sortie structurée, les
numéros des cinq passages les plus utiles pour répondre à la question, du meilleur au moins bon. Mesure hit
rate et MRR, et le temps par question. Un modèle de 3 milliards de paramètres reclasse mal : refais l'essai
après le module 10 avec un modèle hébergé.

## Choisir la stratégie selon la question

La recherche hybride aide surtout quand la question cite un identifiant. Écris une fonction qui détecte un
identifiant (présence de `::`, de `_`, de `--`, d'un `@`, ou d'une majuscule au milieu d'un mot) et qui
choisit la recherche hybride dans ce cas, la recherche vectorielle sinon. Le tableau de la leçon te dit ce
que tu peux espérer. Vérifie.

## Régler la fusion

Fais varier `k` (1, 10, 60, 200) et `depth` (5, 20, 50) dans `hybrid_search`. Puis donne un poids à chaque
classement en multipliant sa contribution. Note les réglages qui changent vraiment le résultat et ceux qui
ne changent rien.

## Améliorer le découpage en mots

`tokenize` garde `whereBelongsTo` entier. Une question qui écrit « where belongs to » ne le retrouve donc
pas. Fais produire au découpage à la fois le mot entier et ses parties (`where`, `belongs`, `to`), et mesure
si la recherche par mots-clés y gagne.
