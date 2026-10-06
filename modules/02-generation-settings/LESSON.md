# 02 · Régler la génération

> Durée : 35 min. Prérequis : module 01.
> Vérifié le 2026-10-06 avec Ollama 0.21, `granite4.1:3b` et `openai` 3.24.

## Objectif

Afficher une réponse au fil de sa production, régler la part de hasard d'un modèle, et constater par
toi-même qu'un modèle invente quand il ne sait pas.

## La notion

### Un modèle écrit un token à la fois

Un modèle de langage ne rédige pas une réponse d'un bloc. Il calcule, pour le texte reçu, la probabilité de
chaque token possible à la suite, en choisit un, l'ajoute au texte, et recommence jusqu'à produire un token
de fin. Tout le reste de ce module découle de cette boucle.

### La température

La température règle la façon de choisir dans ces probabilités. À 0, le modèle prend toujours le token le
plus probable, donc la même question donne la même réponse. Plus elle monte, plus les tokens moins probables
ont leur chance. Voici cinq demandes identiques (« invente un nom de café ») à quatre températures :

```
0    The Cozy Beanery, The Cozy Beanery, The Cozy Beanery, The Cozy Beanery, The Cozy Beanery
0.8  The Brew Haven, The Cozy Beanery, Savannah Café, The Cozy Beanery, The Cozy Beanery
1.5  Coffee Cove, The Nougat Bar, The Beanery, The Cozy Beanery, Cypress Cozy Corner
2.0  Cosmic Brew Grind, Cup of Content Coffee Co., The Nectar Hub, The Cozy Beanery, Java Haven
```

Pour une fonctionnalité qui doit être fiable et testable (extraction de données, réponse à partir de
documents), on travaille à 0 ou tout près. On monte la température quand on veut de la variété, par exemple
pour proposer plusieurs formulations.

### Limiter la longueur

`max_tokens` plafonne la réponse. Le modèle n'en tient pas compte pour conclure, il est coupé net :

```
max_tokens=12  →  "HTTP (Hypertext Transfer Protocol) middleware refers to a"   finish_reason: length
```

Ce paramètre protège d'une réponse interminable et borne le coût. Pour obtenir une réponse courte, il faut
le demander dans le prompt.

### Le streaming

Puisque les tokens sont produits un par un, l'API peut les envoyer au fur et à mesure. Sur la question de
l'exercice, mesurée sur un Mac récent, le premier morceau arrive en 0,1 seconde et la réponse complète en
1,4 seconde, en 128 morceaux. Sur une réponse longue ou un modèle lent, l'écart se compte en dizaines de
secondes. Le streaming ne raccourcit pas le temps total, il supprime l'attente devant un écran vide.

Avec `stream=True`, l'appel renvoie une suite d'événements. Le texte de chacun est dans
`event.choices[0].delta.content`, qui est parfois vide : le dernier événement n'a pas de texte, il porte
la raison de l'arrêt.

### Le prompt système

Le prompt système fixe le comportement pour toute la conversation. Celui de l'exercice demande des réponses
concises, dans la langue de la question. C'est l'endroit où l'on écrira, au module 7, la consigne de ne
répondre qu'à partir des passages fournis.

### Un modèle invente

Pose-lui une question précise sur un outil sorti après son entraînement.

```
> Avec le Laravel AI SDK de Laravel 13, quelle commande Artisan crée un agent et quelle méthode lui
  envoie un prompt ?

La commande Artisan pour créer un agent est `php artisan make:ai-agent`. Pour envoyer un prompt à l'agent,
vous utilisez généralement la méthode `send_prompt()`.
```

La documentation dit `php artisan make:agent` et `->prompt(...)`. La réponse est fausse, écrite sur le même
ton assuré qu'une réponse juste, parce que le modèle produit le texte le plus plausible, pas le texte vrai.
On appelle cela une hallucination. Une température de 0 n'y change rien : elle rend l'erreur reproductible.

Le remède le plus courant est de fournir au modèle les passages de la documentation qui contiennent la
réponse. C'est le RAG, que tu construis des modules 4 à 7.

### Côté Python

Une fonction qui contient `yield` est un générateur, comme en PHP ou avec `function*` en JavaScript. Elle
produit ses valeurs une par une quand on la parcourt avec `for`.

## L'exercice

1. Lance `uv run modules/02-generation-settings/check.py` pour créer ta copie.
2. Écris `stream_answer` : appelle le modèle avec `stream=True` et fais un `yield` de chaque morceau de
   texte non vide.
3. Écris `variants` : envoie le même prompt `n` fois à la température demandée et renvoie les réponses.
4. Lance ta copie. Regarde la réponse arriver, puis compare les noms de café selon la température.
5. Vérifie dans `corpus/docs-*/ai-sdk.md` que la réponse affichée sur le AI SDK est fausse.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- La température règle le hasard : 0 pour ce qui doit être reproductible, plus haut pour de la variété.
- `max_tokens` coupe la réponse, il ne la rend pas concise.
- Le streaming améliore l'attente perçue, pas le temps total.
- Un modèle répond avec assurance même quand il ne sait pas. Il faut lui donner les faits ou vérifier ce
  qu'il produit.

## Dans l'assistant

`stream_answer` servira à afficher les réponses de l'assistant au fil de l'eau. L'hallucination sur le AI SDK
sert de témoin : au module 7, la même question recevra la bonne réponse, sources à l'appui.
