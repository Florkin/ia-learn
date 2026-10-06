# 10 · Modèles hébergés

> Durée : 35 min. Prérequis : module 07, un compte OpenRouter et quelques centimes de crédit.
> Vérifié le 2026-10-06 avec `openai` 3.24 contre Ollama et la liste de prix publique d'OpenRouter.
> La comparaison avec les modèles hébergés n'a pas été exécutée par l'auteur, faute de clé sur sa machine :
> les prix et les calculs de coût ci-dessous sont réels, les observations de qualité sont à faire par toi.

## Objectif

Faire répondre des modèles hébergés à la place du modèle local, sans changer le code de l'assistant, et
comparer qualité, vitesse et coût.

## La notion

### Changer de modèle, c'est changer trois valeurs

Depuis le module 1, tout le code parle le protocole défini par OpenAI. OpenRouter le parle aussi. Passer
d'Ollama à un modèle hébergé revient à changer l'adresse, la clé et le nom du modèle :

```python
OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")          # local
OpenAI(base_url="https://openrouter.ai/api/v1", api_key="sk-or-...")    # hosted
```

OpenRouter est un intermédiaire : un seul compte donne accès aux modèles de dizaines de fournisseurs, au
prix du fournisseur plus une commission. C'est pratique pour comparer. Pour une application en production
qui a choisi son modèle, on s'adresse en général directement au fournisseur.

### Ce qui reste local

La recherche ne change pas. L'index a été construit avec `bge-m3` sur ta machine, la question est
vectorisée sur ta machine, et seuls le prompt et les passages retrouvés partent vers le modèle hébergé.
`compare` retrouve donc les passages une seule fois et envoie le même prompt à chaque modèle : c'est la
condition pour que la comparaison porte sur les modèles et sur rien d'autre.

### Le coût se calcule en tokens

Un modèle hébergé facture séparément les tokens lus et les tokens produits, ces derniers trois à cinq fois
plus cher. Prix publics des trois modèles par défaut du cours, relevés le 2026-10-06, en dollars par million
de tokens :

```
modèle                         entrée   sortie
qwen/qwen3.7-flash               0.03     0.13
openai/gpt-6-luna                0.10     0.50
anthropic/claude-sonnet-5.5      2.00    10.00
```

Pour la première question de l'exercice, le prompt du RAG pèse 1 479 tokens et la réponse du modèle local
145. À ce volume, mille questions coûteraient 0,06 $ avec le premier modèle, 0,22 $ avec le deuxième et
4,41 $ avec le troisième. L'écart entre le moins cher et le plus cher est de 1 à 70.

Deux remarques. Dans un RAG, l'essentiel de la facture vient de l'entrée, donc du nombre et de la taille des
passages : c'est un argument de plus pour une recherche précise. Et les prix changent souvent, si bien que
le cours les lit dans la liste publique d'OpenRouter au lieu de les écrire dans le code.

### Ce qu'on gagne

Un modèle de pointe suit mieux les consignes, raisonne mieux sur plusieurs passages et écrit un meilleur
français. Les réponses du modèle local à la deuxième question de l'exercice donnent de quoi juger : il écrit
« les policies sont utilisés », traduit *logic* par « logiciel », et sur la première question il cite sa
source sous la forme `[passage 1](#)` au lieu de `[1]`. Regarde si les modèles hébergés font ces fautes.

### Ce qu'on paie autrement

- **Les données sortent.** La question et les passages partent chez un tiers. Avec la documentation de
  Laravel, peu importe. Avec les documents d'un client, il faut savoir où le fournisseur héberge, combien de
  temps il conserve les requêtes et s'il s'en sert pour entraîner ses modèles. Ces points se règlent par
  contrat, et ils décident parfois à eux seuls du choix entre local et hébergé.
- **Une dépendance.** Le service peut ralentir, tomber ou plafonner ton débit. Un modèle peut être retiré du
  catalogue : le nom que tu as mis en configuration cessera un jour de répondre.
- **La latence du réseau.** Elle s'ajoute au temps de génération, souvent compensée par des serveurs bien
  plus rapides que ta machine.

Le modèle local a les défauts inverses : qualité plus modeste, matériel à fournir, mais aucun coût par
appel et rien qui sorte.

### Choisir un modèle

La bonne méthode découle du module 8. On part du modèle le moins cher, on le mesure sur son jeu de
questions, et on ne monte en gamme que si la mesure le demande. Beaucoup de tâches d'extraction ou de
classement sont très bien faites par un petit modèle. Le modèle de pointe se justifie pour ce qui demande du
jugement.

## L'exercice

1. Crée une clé sur openrouter.ai et mets-la dans `.env` : `OPENROUTER_API_KEY=sk-or-...`.
2. Lance `uv run modules/10-hosted-models/check.py` pour créer ta copie.
3. Écris `cost`, puis `ask_target`, puis `compare`.
4. Lance ta copie. Elle pose deux questions au modèle local et aux trois modèles hébergés, affiche les
   réponses puis un tableau de durée, de tokens et de coût.
5. Lis les quatre réponses à chaque question. Note pour chacune si elle est juste, si elle cite ses
   passages comme demandé et si le français est correct. Reporte tes observations dans les notes de ton
   `progress.md`, elles serviront à compléter cette leçon.
6. Relance le check jusqu'à ce qu'il passe. Avec la clé, sa dernière étape interroge les modèles hébergés.

Sans clé, l'exercice et le check fonctionnent avec le seul modèle local, mais tu passes à côté de l'objet du
module. L'ensemble de l'exercice coûte moins d'un centime.

## À retenir

- Le protocole est le même partout : on change d'adresse, de clé et de nom de modèle.
- La facture se compte en tokens, entrée et sortie séparées. Dans un RAG, l'entrée domine.
- Hébergé : meilleure qualité, pas de matériel, mais des données qui sortent et une dépendance.
- On choisit le modèle le moins cher qui passe son évaluation.

## Dans l'assistant

Pour faire tourner tout l'assistant sur un modèle hébergé, il suffit de renseigner `CHAT_BASE_URL`,
`CHAT_API_KEY` et `CHAT_MODEL` dans `.env`. Aucune ligne de code ne change.
