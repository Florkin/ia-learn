# 08 · Pour aller plus loin

Exercices facultatifs, sans check.

## Ajouter tes questions

Ajoute cinq cas à `data/golden.jsonl`, tirés de questions que tu t'es réellement posées sur Laravel. Pour
chacun, ouvre la page du corpus et choisis un terme que le bon passage contient forcément. Relance
l'évaluation et lis les nouveaux échecs. Ces cas profitent aux deux apprenants : pousse-les.

## Un modèle comme juge

Pour dix questions, génère la réponse avec `assistant.rag.answer`, puis demande au modèle de la juger avec
une sortie structurée (module 3) : la réponse est-elle entièrement appuyée par les passages fournis, oui ou
non, et pourquoi. Compare ses verdicts aux tiens. Un modèle de 3 milliards de paramètres est un juge
médiocre. Refais l'essai après le module 10 avec un modèle hébergé plus fort et compte les désaccords.

## Mesurer la taille des passages

Construis deux autres index avec `chunk_corpus(max_words=120)` et `chunk_corpus(max_words=600)`, chacun dans
son dossier (`open_collection(DATA_DIR / "exp-120")`), et évalue une recherche sur chacun. L'indexation
prend une à deux minutes par essai sur un Mac récent. Compare hit rate et MRR aux chiffres de la leçon.

## Évaluer le champ `about_laravel`

Le module 3 laissait une question ouverte : peut-on se fier à `about_laravel` ? Les 52 questions du jeu
concernent toutes Laravel. Ajoute vingt questions hors sujet et compte les erreurs dans les deux sens : les
questions légitimes refusées et les questions hors sujet acceptées. Les deux n'ont pas le même coût pour
l'utilisateur.
