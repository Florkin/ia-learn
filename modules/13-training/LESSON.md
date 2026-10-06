# 13 · Entraîner un modèle

> Durée : 40 min. Prérequis : modules 04 et 06. Installation : `uv sync --all-groups`.
> Vérifié le 2026-10-06 avec PyTorch 2.14 sur processeur.

## Objectif

Écrire une boucle d'entraînement, voir un modèle apprendre en trois secondes, puis le faire surapprendre
exprès pour reconnaître le phénomène.

## La notion

### Utiliser un modèle, entraîner un modèle

Depuis le module 1, tu fais de l'inférence : les paramètres du modèle sont figés et tu lui donnes des
entrées. Entraîner, c'est l'inverse. On dispose d'entrées dont on connaît la bonne sortie, et on ajuste les
paramètres jusqu'à ce que le modèle les retrouve.

Tu vas le faire sur un modèle minuscule, parce que la mécanique est exactement celle des grands.

### La tâche

Prédire, à partir de l'embedding d'un passage, la section de la documentation d'où il vient : Security,
Database, Eloquent ORM et six autres. Les données existent déjà. L'index du module 6 contient 3 144 vecteurs
et la section de chacun.

Le modèle est une seule couche linéaire : pour chacune des 9 sections, une somme pondérée des 1024 nombres
du vecteur, soit 9 225 paramètres. `granite4.1:3b` en a 3,4 milliards.

### La perte

Au départ les paramètres sont tirés au hasard et le modèle répond n'importe quoi. Il lui faut une mesure de
son erreur : la perte (*loss*). Pour une classification on utilise l'entropie croisée, qui est faible quand
le modèle donne une forte probabilité à la bonne section et grande quand il se trompe avec assurance.

### La descente de gradient

Pour chaque paramètre, on peut calculer dans quel sens le modifier pour que la perte baisse un peu. C'est
le gradient. L'entraînement répète trois gestes sur un petit lot d'exemples :

```python
loss = loss_function(model(inputs), targets)   # how wrong is the model on this batch?
loss.backward()                                # in which direction should each parameter move?
optimizer.step()                               # move them a little
```

La taille du pas s'appelle le taux d'apprentissage (`lr`). Trop petit, le modèle apprend lentement. Trop
grand, il dépasse la cible et la perte oscille ou explose. Une époque est un passage complet sur les données
d'entraînement.

### Garder des données de côté

Un modèle peut obtenir une perte quasi nulle en mémorisant ses exemples, sans rien avoir compris qui serve
ailleurs. La seule mesure honnête se fait sur des données qu'il n'a jamais vues. On met donc de côté une
partie des exemples, ici 20 %, qui ne servent qu'à mesurer : la validation.

Résultat de l'exercice, sur 2 515 exemples d'entraînement et 629 de validation :

```
époque  perte entraînement  perte validation  précision validation
     1               1.032             1.068                 0.688
     5               0.391             0.454                 0.874
    10               0.242             0.328                 0.900
    30               0.098             0.231                 0.930
```

Après trente époques, le modèle classe correctement 93 % de passages qu'il n'a jamais vus. Pour juger ce
chiffre il faut un point de comparaison : répondre toujours la section la plus fréquente donnerait 40 %.

### Le surapprentissage

Même expérience avec un modèle 57 fois plus gros (une couche cachée de 512 neurones) et seulement 150
exemples :

```
époque  perte entraînement  perte validation  précision validation
    20               0.888             1.174                 0.650
    50               0.101             0.709                 0.789
   100               0.016             0.694                 0.806
   200               0.004             0.749                 0.811
   300               0.002             0.789                 0.814
```

La perte d'entraînement tend vers zéro : le modèle connaît ses 150 exemples par cœur. La perte de validation
baisse jusque vers l'époque 100, puis remonte. À partir de là, chaque époque rend le modèle plus sûr de lui sur
ce qu'il a mémorisé et moins bon sur le reste. C'est le surapprentissage (*overfitting*), et son signe est
toujours le même : les deux courbes se séparent.

Les remèdes : arrêter l'entraînement quand la perte de validation cesse de baisser, ajouter des données,
prendre un modèle plus petit. Avec près de dix-sept fois plus d'exemples, le petit modèle linéaire atteignait
93 %. Celui-ci plafonne à 81 %.

### Ce que mesurent vraiment ces 93 %

Le découpage entre entraînement et validation s'est fait passage par passage, au hasard. Des passages d'une
même page se retrouvent donc des deux côtés. Refais le découpage par page, de sorte qu'aucune page de la
validation n'ait été vue à l'entraînement, et la précision tombe à 33 %, moins bien que la réponse naïve.

Le modèle n'a pas appris ce qu'est un sujet de sécurité ou de base de données. Il a appris à reconnaître
les pages, et la section s'en déduit. Pour classer les passages d'une documentation connue, c'est suffisant
et les 93 % sont réels. Pour classer une page nouvelle, le modèle ne vaut rien. Une mesure ne veut rien dire
tant qu'on n'a pas vérifié que la validation ressemble à l'usage réel, et cette fuite entre entraînement et
validation est l'erreur la plus répandue du domaine.

### Et les grands modèles

Un modèle de langage est entraîné par la même boucle. Sa tâche est de prédire le token suivant d'un texte,
sa perte est l'entropie croisée sur ce token, et l'optimiseur est de la même famille. Ce qui change est
l'échelle : des milliards de paramètres, des milliers de milliards de tokens, des semaines de calcul sur des
centaines de cartes graphiques. Personne ne refait cela pour une application. On part d'un modèle déjà
entraîné, et on l'ajuste, ce qui est le sujet du module suivant.

### Côté Python

PyTorch manipule des tenseurs, des tableaux comme ceux de numpy qui savent en plus calculer des gradients.
`with torch.no_grad():` désactive ce calcul pendant les mesures. `.item()` transforme un tenseur d'une
seule valeur en nombre Python.

## L'exercice

1. Installe les dépendances : `uv sync --all-groups`. Le téléchargement de PyTorch prend quelques minutes.
2. Lance `uv run modules/13-training/check.py` pour créer ta copie.
3. Écris `train` en suivant sa docstring.
4. Lance ta copie. Elle entraîne le modèle linéaire, lui fait classer deux questions, puis lance
   l'expérience de surapprentissage. Repère l'époque où la perte de validation remonte.
5. Passe `lr` à `1.0` dans le premier entraînement et relance, puis à `1e-5`. Remets `1e-2`.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- Entraîner, c'est ajuster des paramètres pour faire baisser une perte sur des exemples connus.
- Trois gestes par lot : calculer la perte, calculer les gradients, déplacer les paramètres.
- Un modèle se juge sur des données de validation, et par rapport à une réponse naïve.
- Quand la perte d'entraînement baisse et que la perte de validation remonte, le modèle surapprend.
- Les modèles de langage sont entraînés de la même façon, à une échelle qu'on ne reproduit pas.

## Dans l'assistant

Une fois la question vectorisée, ce classifieur prédit sa section instantanément. Il pourrait servir de
filtre de recherche au module 6. Le module suivant traite la même tâche en affinant un modèle de
langage, et la comparaison des deux est le point d'arrivée du parcours.
