# 14 · Pour aller plus loin

Exercices facultatifs, sans check.

## Combien d'exemples faut-il ?

Entraîne quatre adaptateurs avec 50, 200, 800 puis tous les exemples d'entraînement, chacun dans son
dossier, et mesure la précision avec `finetune.accuracy`. Trace la courbe. Dans un projet réel, c'est elle
qui dit s'il vaut la peine de produire plus d'exemples.

## Retirer l'indice

Remplace `excerpt(chunk)` par les quarante premiers mots de `chunk.text`, sans le chemin des titres. Le
modèle ne peut plus lire le nom de la page. Réentraîne et compare la précision : l'écart mesure ce que le
modèle tirait du titre.

## Une validation par page

Reprends l'idée du module 13 : mets des pages entières en validation, absentes de l'entraînement. Compare
le résultat à celui du classifieur sur embeddings dans les mêmes conditions (33 %).

## Distiller une tâche du module 3

Le module 3 faisait produire à `granite4.1:3b` une analyse en JSON d'une question. Fais-lui analyser
quelques centaines de questions (les titres de la documentation, tournés en questions, font une bonne
source), garde ses réponses comme exemples, et affine SmolLM2-360M pour qu'il produise le même JSON.
Mesure la part de sorties valides et la part de sorties identiques à celles du grand modèle. C'est l'usage
le plus courant du fine-tuning en entreprise : confier à un petit modèle rapide une tâche étroite qu'un gros
modèle sait faire.

## Fusionner l'adaptateur (Mac)

`uv run python -m mlx_lm fuse --model HuggingFaceTB/SmolLM2-360M-Instruct --adapter-path <dossier de
l'adaptateur> --save-path .data/fused` produit un modèle complet qui contient l'adaptation. Charge-le avec
`mlx_lm.load` et vérifie qu'il répond comme le modèle de base accompagné de son adaptateur.
