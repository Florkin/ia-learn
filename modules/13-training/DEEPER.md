# 13 · Pour aller plus loin

Exercices facultatifs, sans check.

## Arrêter au bon moment

Ajoute à `train` un arrêt anticipé : garde la meilleure perte de validation vue, et arrête quand elle n'a
pas été battue depuis dix époques. Relance l'expérience de surapprentissage et note l'époque d'arrêt.

## Une validation plus honnête

Le découpage du cours mélange les passages au hasard. Des passages de la même page se retrouvent donc des
deux côtés, et reconnaître la page suffit à trouver la section. Refais le découpage par page : toutes les
pages de la validation sont absentes de l'entraînement. La précision chute nettement. Cette fuite entre
entraînement et validation est l'erreur la plus répandue en apprentissage automatique, et elle fait croire
à des modèles bien meilleurs qu'ils ne sont.

## Regarder où le modèle se trompe

Calcule la précision par section, puis la matrice de confusion (combien de passages de la section A sont
classés en B). Les sections rares sont-elles les plus mal classées ? Compare à leur effectif dans les
données d'entraînement.

## Filtrer la recherche avec le classifieur

Prédis la section de chaque question de `data/golden.jsonl`, cherche avec le filtre
`where={"section": ...}` du module 6, et mesure avec `evaluate`. Quand la prédiction est fausse, le bon
passage devient introuvable. Compare le gain et la perte, puis essaie de ne filtrer que lorsque le modèle
est sûr de lui (probabilité de la section prédite au-dessus d'un seuil, avec `torch.softmax`).
