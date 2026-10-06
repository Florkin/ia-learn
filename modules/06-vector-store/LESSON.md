# 06 · Base vectorielle

> Durée : 35 min. Prérequis : module 05.
> Vérifié le 2026-10-06 avec Chroma 1.5 et `bge-m3`.

## Objectif

Ranger les passages et leurs vecteurs dans une base qui persiste sur disque, les mettre à jour sans doublon
et filtrer une recherche par métadonnées.

## La notion

### Ce qu'une base vectorielle apporte

Au module précédent, tout vivait en mémoire et les vecteurs étaient recalculés à chaque lancement. Pour
l'échantillon c'est supportable. Pour les 3 144 passages du corpus, le calcul prend 1 min 40 sur un Mac
récent, et bien plus sur un processeur seul. Une base vectorielle règle quatre problèmes.

- **La persistance.** Les vecteurs sont calculés une fois et relus ensuite.
- **La mise à jour.** Quand une page change, on remplace ses passages par leur identifiant sans tout
  reconstruire.
- **Le filtrage.** On restreint une recherche à une section, un client, une période.
- **L'échelle.** Un index approché évite de comparer la question à chaque vecteur quand il y en a des
  millions.

### Le vocabulaire

Une **collection** est l'équivalent d'une table. Chaque entrée a quatre parties :

```
id         "routing.md#12"
embedding  [0.0123, -0.0456, ...]                 # the vector
document   "To assign middleware to all routes..."  # the text
metadata   {"source": "routing.md", "section": "The Basics", "heading": "Routing > Route Groups > Middleware"}
```

La base renvoie une **distance** plutôt qu'une similarité. Pour le cosinus, la distance vaut 1 moins la
similarité : plus elle est petite, plus le passage est proche.

### Des identifiants stables, et `upsert`

L'identifiant est ce qui permet de retrouver une entrée pour la remplacer. Ceux du cours sont formés du nom
de la page et de la position du passage.

Chroma a deux méthodes d'écriture. `upsert` crée l'entrée ou la remplace si l'identifiant existe. `add`
ignore sans rien dire une entrée dont l'identifiant existe déjà : la base garde l'ancien texte, et tu
cherches pendant une heure pourquoi tes corrections n'apparaissent pas. Pour indexer un corpus qui évolue,
c'est `upsert`.

### Filtrer par métadonnées

La même question, posée sur tout le corpus puis sur une section, puis sur une page :

```
> How do I store something?   filtre : None
  requests.md     HTTP Requests > Files > Storing Uploaded Files
  filesystem.md   File Storage > Storing Files > File Uploads
  cache.md        Cache > Cache Usage > Extending Item Lifetime > Storing Items Forever

> How do I store something?   filtre : {'source': 'session.md'}
  session.md      HTTP Session > Interacting With the Session > Storing Data
  session.md      HTTP Session > Interacting With the Session > Flash Data
  session.md      HTTP Session > Adding Custom Session Drivers > Implementing the Driver
```

Dans une application livrée à un client, le filtre le plus important est celui des droits : les documents
d'un client ou d'un service ne doivent jamais remonter pour un autre. Ce filtre se pose dans le code qui
interroge la base, à partir de l'utilisateur connecté. On ne demande jamais au modèle de faire le tri.

### L'index approché, en trois phrases

Comparer la question à tous les vecteurs devient lent au-delà de quelques centaines de milliers d'entrées.
Les bases construisent alors un graphe où chaque vecteur est relié à ses voisins (HNSW), et la recherche
saute de voisin en voisin au lieu de tout parcourir. Elle peut manquer un bon résultat de temps en temps,
ce qui est le prix de la vitesse. À l'échelle de ce cours, la différence est invisible.

### L'index est lié au modèle d'embeddings

Les vecteurs stockés viennent de `bge-m3`. Si tu changes de modèle, les vecteurs des questions ne sont plus
comparables à ceux de la base et les résultats deviennent absurdes sans aucun message d'erreur. Il faut
réindexer. L'index de référence du cours est rangé dans un dossier qui porte le nom du modèle pour éviter ce
mélange.

### Quelle base choisir

Chroma tourne ici en mode embarqué, comme SQLite : un dossier sur disque, aucun serveur. C'est suffisant
pour apprendre et pour un prototype. Dans une application qui a déjà PostgreSQL, l'extension pgvector met
les vecteurs dans la même base que le reste, avec les transactions et les jointures. Au-delà, il existe des
serveurs spécialisés comme Qdrant. Les notions de ce module sont les mêmes partout.

## L'exercice

1. Lance `uv run modules/06-vector-store/check.py` pour créer ta copie.
2. Écris `build_index` : quatre listes parallèles et un `upsert`.
3. Écris `query_index` : interroge la collection et reconstruis des `Chunk`.
4. Lance ta copie deux fois de suite. La seconde fois, le compteur « avant indexation » n'est plus à zéro :
   l'index a survécu au programme.
5. Relance le check jusqu'à ce qu'il passe.

Ton index est rangé dans `.data/`, hors de git. Tu peux supprimer ce dossier à tout moment, il sera
reconstruit.

## À retenir

- Une base vectorielle stocke identifiant, vecteur, texte et métadonnées, et les garde sur disque.
- Des identifiants stables et `upsert` permettent de mettre à jour un corpus sans doublon.
- Les filtres de métadonnées restreignent la recherche. Celui des droits d'accès se pose dans le code.
- Un index n'est valable que pour le modèle d'embeddings qui l'a produit.

## Dans l'assistant

À partir du module suivant, l'assistant cherche dans l'index de référence de tout le corpus. Construis-le
maintenant, une fois pour toutes :

```shell
uv run python -m assistant.store
```
