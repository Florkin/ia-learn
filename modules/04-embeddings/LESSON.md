# 04 · Embeddings

> Durée : 35 min. Prérequis : module 01.
> Vérifié le 2026-10-06 avec Ollama 0.21, `bge-m3`, `openai` 3.24 et `numpy` 2.5.

## Objectif

Transformer des textes en vecteurs, mesurer leur proximité, et t'en servir pour classer des phrases par
rapport à une question.

## La notion

### Un texte devient une liste de nombres

Un modèle d'embeddings prend un texte et renvoie un vecteur, une liste de nombres de longueur fixe. Celui du
cours, `bge-m3`, en produit 1024 :

```
"route"  →  [-0.0161, -0.0067, 0.0199, 0.0068, -0.0302, ...]   # 1024 values
```

Aucun de ces nombres n'a de sens pris isolément. Ce qui compte est la position du vecteur par rapport aux
autres : le modèle a été entraîné pour que deux textes de sens voisin donnent deux vecteurs voisins.

C'est un autre modèle que celui qui discute avec toi. Il est plus petit, ne génère rien, et se contente de
lire. L'API a un point d'entrée distinct, `/v1/embeddings`.

### Mesurer la proximité : la similarité cosinus

On compare deux vecteurs par l'angle qu'ils forment. Le cosinus de cet angle vaut 1 quand ils pointent dans
la même direction, 0 quand ils sont perpendiculaires, -1 quand ils sont opposés.

```
cos(a, b) = (a · b) / (‖a‖ × ‖b‖)
```

Le numérateur est le produit scalaire (`np.dot`), le dénominateur le produit des longueurs
(`np.linalg.norm`). Diviser par les longueurs rend la mesure indépendante de la taille des vecteurs : seule
la direction compte.

### Ce que les scores veulent dire

Quelques mesures faites avec `bge-m3` :

```
"How do I hash a password?"  vs  "Comment hacher un mot de passe ?"   0.859
"How do I hash a password?"  vs  "The weather is nice today."         0.409
```

La même question dans deux langues obtient un score élevé, parce que `bge-m3` est multilingue. C'est ce qui
permettra de poser des questions en français sur une documentation en anglais.

Deux phrases sans rapport obtiennent 0,41 et non 0. Un score ne se lit donc jamais seul. On classe des
candidats entre eux, et le seuil à partir duquel un résultat est jugé pertinent dépend du modèle.

### Le sens plutôt que les mots

Classement de cinq phrases pour la question « How do I limit the number of requests per minute? » :

```
0.756  Rate limiters restrict how many requests a client may send in a given amount of time.
0.718  Les limiteurs de débit plafonnent le nombre de requêtes qu'un client peut envoyer.
0.632  You may limit the number of results returned from a query using the limit method.
0.382  Blade is the templating engine included with Laravel.
0.355  The Hash facade provides secure Bcrypt and Argon2 hashing for storing user passwords.
```

La troisième phrase partage le plus de mots avec la question (« limit the number of ») et arrive pourtant
derrière deux phrases qui parlent du bon sujet, dont une en français. Une recherche par mots-clés aurait fait
l'inverse.

### Ça se trompe aussi

```
> How do I throttle an API?
0.495  Blade is the templating engine included with Laravel.
0.418  Rate limiters restrict how many requests a client may send in a given amount of time.
```

Sur une question courte, formulée avec un mot que le modèle relie mal au sujet, la phrase sur Blade passe
devant. Les scores sont serrés et le premier résultat est faux. Garde cet exemple en tête : il justifie de
mesurer la recherche (module 8) et de la combiner avec des mots-clés (module 9).

### Trois règles à connaître

- La question et les documents passent par le même modèle. Des vecteurs issus de deux modèles différents ne
  se comparent pas.
- Changer de modèle d'embeddings oblige à recalculer tous les vecteurs.
- Un modèle d'embeddings a une longueur d'entrée maximale (8192 tokens pour `bge-m3`). Le texte en trop est
  ignoré, ce qui est une des raisons de découper les documents au module suivant.

### Côté Python

`numpy` manipule des tableaux de nombres. Un vecteur est un tableau à une dimension, une liste de vecteurs
un tableau à deux dimensions dont `shape` vaut `(nombre de textes, 1024)`. `np.array(liste)` convertit une
liste Python en tableau.

## L'exercice

1. Lance `uv run modules/04-embeddings/check.py` pour créer ta copie.
2. Écris `cosine_similarity` avec `np.dot` et `np.linalg.norm`.
3. Écris `embed` : un appel à l'API pour toute la liste, puis un tableau numpy à deux dimensions.
4. Écris `rank` : calcule les vecteurs de la question et des candidats, puis trie par similarité
   décroissante. Un seul appel à `embed` suffit pour tous les textes.
5. Lance ta copie et compare les trois classements. Ajoute tes propres phrases et questions.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- Un embedding est un vecteur qui place un texte dans un espace où la proximité suit le sens.
- La similarité cosinus compare la direction de deux vecteurs.
- Les scores se comparent entre eux, pas à une échelle absolue.
- Un modèle multilingue rapproche une question et un passage écrits dans deux langues.
- La recherche par le sens se trompe parfois. Elle se mesure.

## Dans l'assistant

`embed` sert à indexer la documentation et à vectoriser chaque question. Sa version de référence découpe les
longues listes en lots de 64 textes pour ne pas envoyer des milliers de passages en une requête.
