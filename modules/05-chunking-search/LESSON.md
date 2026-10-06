# 05 · Découper et chercher

> Durée : 45 min. Prérequis : module 04.
> Vérifié le 2026-10-06 avec `bge-m3` et la documentation Laravel 13 (commit `07b6889f`).

## Objectif

Découper des pages de documentation en passages, puis retrouver les passages les plus proches d'une question
en la comparant à tous les vecteurs.

## La notion

### Pourquoi découper

La page sur le routage fait 5 000 mots. Si tu en fais un seul vecteur, il représente la moyenne de tout ce
que la page aborde : il ressemble un peu à toutes les questions sur les routes et précisément à aucune. Et
une fois la page retrouvée, il faudrait donner 5 000 mots au modèle pour une réponse qui tient dans un
paragraphe.

On indexe donc des passages. Un passage qui traite d'une seule chose a un vecteur net, et il coûte peu de
tokens quand on le transmet au modèle.

### Où couper

- **À taille fixe**, tous les 200 mots. C'est simple et ça marche sur n'importe quel texte, mais la coupe
  tombe au milieu d'une phrase ou d'un exemple de code.
- **Selon la structure**, à chaque titre. L'auteur a déjà découpé son texte en unités de sens, autant s'en
  servir. C'est le bon choix pour une documentation en markdown, et celui de l'exercice.

On y ajoute une taille maximale. Une section plus longue est recoupée entre deux paragraphes, sans jamais
ouvrir un bloc de code en deux.

Sur les 76 pages du corpus, ce découpage donne 3 144 passages, d'une longueur médiane de 76 mots et d'au
plus 300.

### Trop petit, trop grand

Un passage trop court perd son contexte : « Cette méthode accepte aussi un tableau » ne dit plus de quelle
méthode on parle. Un passage trop long retombe dans le défaut de la page entière. La bonne taille dépend du
corpus et se règle en mesurant, ce que tu feras au module 9.

### Redonner son contexte au passage

Le premier paragraphe de la section sur les middlewares de groupe commence par « To assign middleware to all
routes within a group... ». Rien n'y dit qu'on parle du routage. On conserve donc avec chaque passage le
chemin de ses titres :

```
Routing > Route Groups > Middleware
```

C'est ce chemin suivi du texte qui est transformé en vecteur (propriété `content` de `Chunk`). Le coût est
de quelques mots par passage, et le gain en précision est net.

### Nettoyer avant de découper

Chaque page de la documentation commence par un sommaire et sème des ancres HTML (`<a name="...">`). Ce
sont des lignes sans information qui produiraient des passages inutiles. La fonction `clean` les retire.
Ce nettoyage est propre à chaque corpus : un export de wiki ou des PDF convertis ont d'autres parasites, et
on les découvre en lisant les passages produits.

Un piège classique du markdown : dans un bloc de code shell, `# Clear the whole cache` est un commentaire.
Un découpage naïf en fait un titre.

### Chercher sans base de données

Avec les vecteurs de tous les passages dans un tableau, chercher revient à calculer la similarité de la
question avec chaque ligne et à garder les meilleures. Comme les vecteurs de `bge-m3` sont de longueur 1,
un produit de matrices suffit : `vectors @ query_vector` donne les 3 144 scores d'un coup.

```
> Comment appliquer un middleware à un groupe de routes ?
  0.765  routing.md     Routing > Route Groups > Middleware
  0.748  middleware.md  Middleware > Registering Middleware > Assigning Middleware to Routes > Excluding Middleware
  0.746  middleware.md  Middleware > Registering Middleware > Middleware Groups
```

Cette recherche exhaustive répond en quelques millisecondes jusqu'à des centaines de milliers de passages.
Une base vectorielle n'apporte pas une meilleure recherche. Elle apporte la persistance, les filtres et le
passage à l'échelle, sujets du module suivant.

### Côté Python

`@dataclass(frozen=True)` déclare un objet-valeur immuable, l'équivalent d'une classe `readonly` en PHP.
`@property` expose une méthode comme un attribut. `a @ b` est le produit matriciel de numpy.

## L'exercice

1. Lance `uv run modules/05-chunking-search/check.py` pour créer ta copie.
2. Écris `chunk_markdown` en suivant les étapes de sa docstring. `clean` et `pack_paragraphs` sont fournis.
3. Écris `search` : vecteur de la question, scores, puis les `k` meilleurs.
4. Lance ta copie. Elle découpe sept pages de la documentation, calcule les vecteurs et te laisse chercher.
   Essaie en français et en anglais.
5. Relance le check jusqu'à ce qu'il passe.

Le check donne le chemin de titres obtenu quand il diffère du chemin attendu. Lis-le, c'est le moyen le plus
rapide de trouver une erreur dans la gestion des niveaux.

## À retenir

- On indexe des passages, pas des documents entiers.
- La structure du document (ses titres) donne les meilleures coupes. On borne la taille par-dessus.
- Chaque passage garde le chemin de ses titres pour rester compréhensible seul.
- Le nettoyage est propre au corpus et se vérifie en lisant les passages.
- Une recherche exhaustive par produit de matrices suffit longtemps.

## Dans l'assistant

`chunk_corpus` découpe toute la documentation avec ta logique de `chunk_markdown`. Ces passages sont l'unité
que l'assistant indexe, retrouve et cite.
