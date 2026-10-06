# 09 · Améliorer la recherche

> Durée : 40 min. Prérequis : modules 03 et 08.
> Vérifié le 2026-10-06 avec `bge-m3`, `granite4.1:3b` et le jeu de 52 questions.

## Objectif

Combiner la recherche par le sens et la recherche par mots-clés, mesurer l'effet, et décider avec des
chiffres si le changement mérite d'entrer dans l'assistant.

## La notion

### Le point faible de la recherche vectorielle

Le module 8 a laissé deux constats. La question sur `QUEUE_CONNECTION` échoue : les passages remontés
parlent bien de connexions de files d'attente, mais aucun ne contient la variable. Et le bon passage n'est
premier que pour 61 % des questions.

Les embeddings saisissent le sens d'une phrase. Un identifiant exact, un code d'erreur ou une référence
produit n'ont pas de sens à saisir : ils sont présents dans le passage ou ils ne le sont pas.

### La recherche par mots-clés : BM25

BM25 est la formule qui classe les résultats dans Elasticsearch, OpenSearch ou la recherche plein texte de
PostgreSQL. Elle donne un score élevé à un passage qui contient les mots de la question, avec trois
correctifs.

- Un mot rare dans le corpus compte plus qu'un mot fréquent. `QUEUE_CONNECTION` pèse lourd, `the` ne pèse
  rien.
- Répéter un mot dix fois ne vaut pas dix fois plus qu'une seule occurrence.
- Un passage long est pénalisé, puisqu'il a plus de chances de contenir n'importe quel mot.

La classe `BM25` de `assistant/retrieval.py` tient en trente lignes. Elle découpe le texte en gardant les
identifiants entiers : `whereBelongsTo` et `APP_DEBUG` sont chacun un seul mot.

### Le piège de la langue

La documentation est en anglais et les questions sont en français. Les mots de « Comment hacher un mot de
passe ? » n'apparaissent nulle part dans le corpus. Sans précaution, la recherche par mots-clés ne retrouve
un bon passage que pour 46 % des questions, essentiellement celles qui citent un identifiant.

Le remède existe depuis le module 3 : `analyze_question` produit une requête de recherche en anglais
(« how to hash a password in laravel »). Avec elle, les mots-clés seuls montent à 88 %.

### Fusionner deux classements

Les deux recherches rendent chacune une liste classée. Leurs scores ne sont pas comparables, une similarité
cosinus d'un côté, un score BM25 sans borne de l'autre. La fusion par rangs réciproques (*reciprocal rank
fusion*, RRF) ignore donc les scores et ne regarde que les positions :

```
score(passage) = somme, sur chaque classement où il apparaît, de 1 / (k + rang)
```

Un passage bien classé dans les deux listes passe devant un passage premier dans une seule. La constante
`k`, fixée à 60 par convention, évite qu'une première place écrase tout le reste.

### Les chiffres

Cinq stratégies sur les 52 questions, avec cinq passages retrouvés :

```
stratégie                      hit@1  hit@5  MRR
vectorielle                    0.615  0.981  0.765
mots-clés, question brute      0.288  0.462  0.351
mots-clés, question réécrite   0.500  0.885  0.646
hybride, question brute        0.596  0.846  0.679
hybride, question réécrite     0.769  0.962  0.843
```

Trois lectures.

**Une recherche hybride mal faite dégrade le système.** Fusionner la recherche vectorielle avec des
mots-clés en français fait tomber le hit rate de 98 % à 85 %. Un mauvais classement tire les bons résultats
vers le bas. Ajouter une technique réputée n'améliore rien par principe.

**Bien faite, elle place le bon passage plus haut.** Avec la question réécrite, le bon passage est premier
pour 77 % des questions au lieu de 61 %, et `QUEUE_CONNECTION` est retrouvé.

**Elle a un prix.** Le hit rate à 5 recule d'une question. Dans le détail, seize questions gagnent des
places et six en perdent, dont « Comment garder un utilisateur connecté après la fermeture du navigateur ? »
qui passe du premier rang à l'absence. Et chaque recherche demande maintenant un appel au modèle pour la
réécriture : 0,56 seconde par question au lieu de 0,06.

### Décider

Le chiffre à regarder dépend de l'usage. L'assistant donne cinq passages au modèle, donc ce qui compte pour
lui est le hit rate à 5, où la recherche vectorielle seule fait aussi bien, plus vite et plus simplement.
`assistant.rag.answer` reste sur la recherche vectorielle. La recherche hybride prendrait l'avantage si l'on
ne transmettait qu'un ou deux passages pour réduire le coût, si l'on affichait directement les résultats à
l'utilisateur, ou sur un corpus rempli de références et de codes.

C'est le déroulé à retenir pour n'importe quel réglage : une hypothèse tirée des échecs, un changement, une
mesure sur le jeu complet, une lecture question par question, puis une décision qui tient compte du coût.

### Le reclassement, en bref

L'autre grande technique s'appelle le reclassement (*reranking*). On retrouve large, vingt à cinquante
passages, puis un second modèle lit la question et chaque passage ensemble et leur donne une note. Ce modèle
est plus précis qu'une comparaison de vecteurs parce qu'il voit les deux textes en même temps, et plus lent
pour la même raison, d'où son usage sur une courte liste seulement. Les approfondissements en proposent une
version avec le modèle de conversation.

## L'exercice

1. Lance `uv run modules/09-better-retrieval/check.py` pour créer ta copie.
2. Écris `reciprocal_rank_fusion`.
3. Écris `hybrid_search` en suivant les quatre étapes de sa docstring.
4. Lance ta copie. Elle évalue les cinq stratégies, ce qui prend environ une minute, et affiche le tableau.
   Compare-le à celui de la leçon.
5. Relance le check jusqu'à ce qu'il passe. Sa dernière étape rejoue l'évaluation complète.

## À retenir

- La recherche vectorielle comprend le sens, la recherche par mots-clés retrouve les termes exacts.
- BM25 favorise les mots rares et pénalise les passages longs.
- La fusion par rangs réciproques combine des classements sans comparer leurs scores.
- Une question et un corpus dans deux langues différentes cassent la recherche par mots-clés.
- Une amélioration se décide sur une mesure, lue question par question, coût compris.

## Dans l'assistant

`hybrid_search` rejoint la boîte à outils de l'assistant sans devenir son réglage par défaut. Le module 12
la proposera au modèle comme un outil parmi d'autres.
