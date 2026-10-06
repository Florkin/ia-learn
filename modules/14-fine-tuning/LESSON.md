# 14 · Fine-tuning

> Durée : 45 min, entraînement compris. Prérequis : module 13. Installation : `uv sync --all-groups`.
> Vérifié le 2026-10-06 sur un Mac M5 Pro avec `mlx-lm` 0.32, puis avec PyTorch 2.14, `transformers` 5.18
> et `peft` 0.21 (carte graphique Apple, puis processeur seul). La variante PyTorch n'a pas été exécutée par
> l'auteur sur Windows, sur Linux ni sur une carte NVIDIA.

## Objectif

Affiner un petit modèle de langage sur une tâche, mesurer ce qu'il a appris, et savoir placer le
fine-tuning parmi les autres façons d'adapter un modèle.

## La notion

### Trois façons d'adapter un modèle

- **Le prompt.** On explique la tâche, on donne des exemples. Rien à entraîner, résultat immédiat.
- **Le RAG.** On apporte au modèle, au moment de la question, les connaissances qui lui manquent.
- **Le fine-tuning.** On poursuit l'entraînement du modèle sur ses propres exemples. Ses paramètres
  changent.

Le fine-tuning modifie un comportement. Il convient mal aux connaissances : une documentation qui évolue
se réindexe en deux minutes, alors qu'un modèle affiné dessus serait à réentraîner à chaque version, sans
pouvoir citer ses sources. Il convient à ce qui ne se décrit pas dans un prompt : un format ou un ton tenus
sans faille, une classification selon des catégories maison, ou un petit modèle bon marché à qui on apprend
une seule tâche qu'on confiait à un gros.

### La tâche

La même qu'au module 13 : donner la section de la documentation d'où vient un passage. Ce classement est
arbitraire, rien dans le texte d'une page sur le cache ne dit qu'elle est rangée dans « Digging Deeper ».
Un prompt ne peut donc pas l'enseigner. Avec la seule consigne, mesuré sur 100 passages :

```
granite4.1:3b (3,4 milliards de paramètres)     28 %   il répond « The Basics » une fois sur deux
SmolLM2-360M (360 millions de paramètres)        7 %   il ne respecte même pas le format
```

Le petit modèle répond `Section: AI`, `` `wordCount` `` ou recopie un titre. C'est lui qu'on va affiner.

### LoRA

Réentraîner les 362 millions de paramètres du modèle est lourd, et produit une copie complète du modèle
pour chaque tâche. LoRA (*low-rank adaptation*) gèle les paramètres d'origine et ajoute de petites matrices
dans les couches d'attention. On n'entraîne qu'elles :

```
Trainable parameters: 0.600% (2.171M/361.821M)
```

Le résultat s'appelle un adaptateur. Celui de l'exercice pèse 9 Mo, à côté d'un modèle de base de 693 Mo.
On peut garder un adaptateur par tâche et les brancher sur le même modèle.

### Les données sont le vrai travail

Un exemple d'entraînement est une conversation dont la dernière réplique est la réponse attendue :

```json
{"messages": [
  {"role": "system", "content": "Classify the passage of the Laravel documentation into one of these sections: AI, Architecture Concepts, ... Reply with the section name only."},
  {"role": "user", "content": "Cache > Cache Usage > Storing Items in the Cache You may use the put method on the Cache facade..."},
  {"role": "assistant", "content": "Digging Deeper"}
]}
```

Ici les exemples se fabriquent tout seuls, puisque chaque passage connaît sa section : 2 830 pour
l'entraînement, 314 pour la validation. Dans un projet réel, c'est l'étape qui coûte. Il faut des centaines
d'exemples justes, représentatifs des cas réels, et un jeu de validation tenu à l'écart. Un modèle affiné
sur des exemples médiocres reproduit fidèlement leur médiocrité.

### L'entraînement

C'est la boucle du module 13 : calculer la perte, calculer les gradients, déplacer les paramètres. La perte
ne porte que sur les tokens de la réponse, le prompt est masqué. Deux cents itérations de huit exemples
suffisent :

```
iter   train_loss
  25        0.706
  50        0.121
 100        0.034
 200        0.001
```

### Le résultat

```
attendu          avant affinage                         après affinage
Database         Database: Getting Started > Running    Database
Testing          Eloquent ORM                           Testing
Digging Deeper   `Str::ucfirst()`                       Digging Deeper
Testing          Section: AI                            Testing
The Basics       Security                               The Basics

Bonnes réponses sur 100 passages : 7 % avant, 100 % après
```

En une demi-minute d'entraînement, le modèle a appris le format et le classement.

### Deux moteurs

Le cours fournit deux moteurs qui font la même chose avec les mêmes données. `FINETUNE_BACKEND` dans `.env`
choisit entre eux, et le défaut dépend de ta machine.

```
moteur   pour quelle machine              durée des 200 itérations (Mac M5 Pro)    résultat
mlx      Mac Apple Silicon                34 s                                      100 %
peft     toute machine, avec PyTorch      113 s sur la carte graphique Apple        95 à 98 %
                                          7 min sur le processeur seul
```

Sur un PC sans carte graphique, compte plutôt quinze à vingt minutes. Cette durée est une estimation et n'a
pas été mesurée. Tu peux la diviser par deux avec `FINETUNE_ITERS=100` dans `.env`, pour une précision
mesurée de 83 %. Avec une carte NVIDIA, le moteur `peft` l'utilise sans réglage.

Le moteur `peft` tient en une centaine de lignes dans `assistant/finetune_peft.py`. Sa boucle
d'entraînement est celle que tu as écrite au module 13.

### Fallait-il un fine-tuning ?

La même tâche, quatre approches :

```
approche                                   bonnes réponses   entraînement          modèle à faire tourner
répondre toujours la section majoritaire        40 à 46 %    aucun                 aucun
consigne seule, modèle de 3,4 milliards              28 %    aucun                 2 Go
classifieur sur embeddings (module 13)               93 %    3 s sur processeur    9 225 paramètres
petit modèle de langage affiné (ce module)     95 à 100 %    34 s à 20 min         360 millions de paramètres
```

Les mesures viennent d'échantillons de validation différents et se comparent à quelques points près. La
conclusion ne change pas : pour ranger un texte dans une catégorie, un classifieur sur des embeddings fait
presque aussi bien pour mille fois moins de calcul. Le fine-tuning d'un modèle de langage se justifie quand
la sortie est du texte ou une structure à générer, pas une étiquette.

La réserve du module 13 vaut aussi ici. L'extrait donné au modèle commence par le titre de la page, et les
passages d'une même page sont répartis entre entraînement et validation. Le modèle a appris à quelle section
appartient chaque page. Les 100 % mesurent cela, pas une compréhension des sujets.

### Dans quel ordre essayer

D'abord le prompt, puis des exemples dans le prompt. Si le modèle manque de connaissances, un RAG. Le
fine-tuning vient en dernier, quand on dispose de centaines d'exemples, d'une évaluation, et d'un écart
mesuré que les autres approches n'ont pas comblé. Il ajoute des coûts durables : produire et maintenir les
données, réentraîner quand le modèle de base change, héberger son propre modèle.

## L'exercice

1. Installe les dépendances si ce n'est pas fait : `uv sync --all-groups`.
2. Lance `uv run modules/14-fine-tuning/check.py` pour créer ta copie.
3. Écris `build_examples` : un exemple de conversation par passage.
4. Écris `split_examples` : mélange reproductible, puis coupe.
5. Lance ta copie. Elle télécharge le modèle de base (693 Mo) au premier lancement, mesure ses réponses,
   l'affine et compare. Regarde la perte baisser pendant l'entraînement.
6. Relance le check jusqu'à ce qu'il passe. Sa dernière étape entraîne un adaptateur, puis le réutilise
   aux lancements suivants tant que tes données ne changent pas.

Sur Mac, refais l'essai avec `FINETUNE_BACKEND=peft` dans `.env` pour comparer les deux moteurs.

## À retenir

- Le fine-tuning change un comportement. Les connaissances qui bougent relèvent du RAG.
- LoRA n'entraîne qu'une petite fraction des paramètres et produit un adaptateur léger.
- La qualité des exemples décide du résultat, et leur préparation est l'essentiel du travail.
- Une tâche de classement se traite d'abord avec un classifieur sur embeddings.
- Ordre d'essai : prompt, exemples, RAG, puis fine-tuning si une mesure le justifie.

## Dans l'assistant

Le parcours s'arrête ici. L'assistant sait répondre à partir de la documentation, citer ses sources, se
mesurer, changer de modèle, chercher de lui-même, et tu sais ce que coûterait de lui apprendre un
comportement nouveau. Les modules suivants s'ajoutent à la demande, la marche à suivre est dans le README.
