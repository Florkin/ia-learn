# 08 · Évaluer

> Durée : 35 min. Prérequis : module 07.
> Vérifié le 2026-10-06 avec `bge-m3`, Chroma 1.5 et le jeu de 52 questions de `data/golden.jsonl`.

## Objectif

Remplacer « ça a l'air de marcher » par deux chiffres, et savoir lire les échecs qu'ils cachent.

## La notion

### Pourquoi mesurer

Un RAG a beaucoup de réglages : taille des passages, modèle d'embeddings, nombre de passages, méthode de
recherche, prompt. Chaque changement améliore certaines questions et en dégrade d'autres. En testant trois
questions à la main après chaque modification, tu ne vois que celles que tu as en tête, et tu règles à
l'aveugle.

L'évaluation consiste à fixer une liste de questions dont on connaît la bonne réponse, puis à rejouer toute
la liste à chaque changement.

### Le jeu de questions

`data/golden.jsonl` contient 52 cas, un par ligne :

```json
{"question": "Comment définir une route avec un paramètre optionnel ?", "sources": ["routing.md"], "contains": ["optional"]}
{"question": "Que fait la règle prohibited_unless ?", "sources": ["validation.md"], "contains": ["prohibited_unless"]}
```

Chaque cas dit ce qu'est un bon résultat : un passage qui vient d'une des pages de `sources` et qui contient
un des termes de `contains`. La fonction `is_relevant` applique cette règle.

Le jeu mélange volontairement plusieurs sortes de questions : des demandes courantes, des reformulations qui
n'emploient pas les mots de la documentation (« éviter qu'une tâche planifiée se lance deux fois »), des
questions en anglais et des identifiants exacts (`whereBelongsTo`, `APP_DEBUG`).

### Juger la pertinence

Se contenter de la bonne page serait trop indulgent : la page sur la validation donne 180 passages, et en
retrouver un quelconque ne prouve rien. Exiger un terme précis est plus sévère, parfois
trop. La question « Comment tester qu'une route renvoie un code 200 ? » attendait d'abord
`assertStatus(200)`, alors que le passage sur `assertOk` y répond aussi bien. Le cas accepte maintenant les
deux.

Retiens le réflexe : devant un échec, on vérifie d'abord l'étiquette. Une partie des échecs d'une première
évaluation sont des erreurs du jeu de questions, pas du système.

### Deux mesures

Pour chaque question, on note le rang du premier passage pertinent parmi les `k` retrouvés, ou `None`.

- Le **hit rate à k** est la part des questions qui ont un passage pertinent dans les `k` premiers. Il dit
  si le modèle reçoit de quoi répondre.
- Le **MRR** (*mean reciprocal rank*) est la moyenne de `1 / rang`. Un bon passage en première position
  compte 1, en deuxième 0,5, en cinquième 0,2, absent 0. Il dit si le bon passage arrive tôt.

La recherche vectorielle de l'assistant, mesurée sur les 52 questions :

```
k=1   hit rate 0.615
k=3   hit rate 0.904
k=5   hit rate 0.981   MRR 0.765
```

Avec cinq passages, le modèle a presque toujours de quoi répondre. En revanche le bon passage n'est premier
que six fois sur dix. C'est là qu'il reste de la marge, et ces chiffres servent de point de départ au module
suivant.

### Lire les échecs

Un chiffre global ne dit pas quoi corriger. La liste des échecs le dit. Il y en a un seul à k=5 :

```
À quoi sert QUEUE_CONNECTION ?
    queues.md   Queues > Introduction > Connections vs. Queues
    queues.md   Queues > Dispatching Jobs > Job Chaining > Chain Connection and Queue
    events.md   Events > Queued Event Listeners > Customizing The Queue Connection, Name, & Delay
```

La recherche a compris le sujet, les connexions de files d'attente, mais aucun des passages remontés ne
contient la variable demandée. Les embeddings saisissent le sens et traitent mal un identifiant exact.
Une recherche par mots-clés fait l'inverse, d'où l'idée de combiner les deux.

### Ce que ces chiffres ne mesurent pas

Ils évaluent la recherche, pas la réponse. C'est un choix : la recherche se mesure vite, sans appeler le
modèle de conversation, et de façon reproductible. Évaluer la réponse elle-même (est-elle fidèle aux
passages, complète, bien citée ?) demande une relecture humaine ou un second modèle qui joue le juge. Les
approfondissements proposent un premier essai.

Deux précautions. Avec 52 questions, une seule question pèse 1,9 point : un écart de deux points entre deux
réglages n'est pas un résultat. Et un système réglé pour briller sur ses 52 questions finit par être bon
sur celles-là seulement, donc le jeu doit continuer à grandir avec les vraies questions des utilisateurs.

## L'exercice

1. Lance `uv run modules/08-evaluation/check.py` pour créer ta copie.
2. Écris `first_relevant_rank`, `hit_rate` et `mrr`. Chacune tient en quelques lignes.
3. Écris `evaluate`, qui les assemble.
4. Lance ta copie : elle mesure la recherche vectorielle et affiche les échecs avec les passages retrouvés.
5. Change `k=5` en `k=1` puis `k=3` dans le bloc final et relance.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- Une évaluation est une liste de questions avec, pour chacune, la définition d'un bon résultat.
- Le hit rate dit si le bon passage est retrouvé, le MRR s'il arrive tôt.
- La liste des échecs vaut plus que le chiffre global. On vérifie l'étiquette avant d'accuser le système.
- La recherche s'évalue séparément de la génération, et bien plus facilement.
- Un petit jeu de questions donne des chiffres bruités.

## Dans l'assistant

`evaluate` devient l'instrument de mesure de tout ce qui suit. Aucun changement de la recherche n'entre
dans l'assistant sans être passé par elle.
