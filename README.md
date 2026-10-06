# ia-learn

Un parcours pratique d'IA engineering pour développeurs. En quatorze sessions de 30 à 45 minutes, tu
construis toi-même, couche après couche, un assistant qui répond à des questions sur la documentation de
Laravel : appel à un modèle, embeddings, base vectorielle, RAG, évaluation, modèles hébergés, LangChain,
agents, entraînement et fine-tuning.

Chaque brique est d'abord écrite à la main, avec le minimum de code, avant de voir ce qu'un framework en
fait.

## Installation

Il te faut [uv](https://docs.astral.sh/uv/) et [Ollama](https://ollama.com). uv installe la bonne version de
Python tout seul.

```shell
git clone https://github.com/Florkin/ia-learn.git && cd ia-learn
uv sync                          # base dependencies, a few seconds
ollama pull granite4.1:3b        # chat model, 2.1 GB
ollama pull bge-m3               # embedding model, 1.2 GB
```

Copie `.env.example` vers `.env` et renseigne ton prénom, en minuscules et sans espace :

```
LEARNER=tristan
```

Vérifie que tout répond en lançant le premier check. Il doit créer ton exercice puis échouer sur une
fonction qui n'est pas encore écrite :

```shell
uv run modules/01-first-call/check.py
```

Si le message parle d'un modèle injoignable, lance Ollama (`ollama serve`, ou ouvre l'application).

### Machine modeste ou sans carte graphique

Les deux modèles locaux tournent sur un ordinateur portable ordinaire, plus lentement. Si c'est trop lent,
`.env.example` montre comment pointer la conversation et les embeddings vers OpenRouter dès le module 1,
pour quelques centimes sur tout le parcours. Le module 14 a deux moteurs, `mlx` pour les Mac Apple Silicon
et `peft` pour toutes les machines, choisis automatiquement.

Sur une machine qui a beaucoup de mémoire, Ollama réserve toute la fenêtre de contexte du modèle, soit 21 Go
pour `granite4.1:3b` sur un Mac de 64 Go. Lancer le serveur avec `OLLAMA_CONTEXT_LENGTH=8192 ollama serve`
ramène cela à peu de chose sans gêner le cours.

## Une session

1. Lis la leçon du module : `modules/04-embeddings/LESSON.md`. Dix minutes.
2. Lance son check : `uv run modules/04-embeddings/check.py`. La première fois, il copie le squelette de
   l'exercice dans `learners/<ton prénom>/04-embeddings.py` et te dit ce qui manque.
3. Complète ta copie et lance-la pour voir le résultat : `uv run learners/<ton prénom>/04-embeddings.py`.
4. Relance le check. Quand il passe, il inscrit le module dans `learners/<ton prénom>/progress.md`.

La solution de chaque module est sa brique dans le dossier `assistant/`. Regarde-la après avoir cherché.
Les modules suivants s'appuient sur ces briques de référence et jamais sur ta copie : un exercice sauté ne
bloque pas la suite.

Chaque module a aussi un `DEEPER.md`, des approfondissements facultatifs à reprendre quand tu veux.

## Le parcours

| # | Module | Ce que tu construis | Durée |
|---|---|---|---|
| | **Parler à un modèle** | | |
| 01 | [Premier appel](modules/01-first-call/LESSON.md) | Messages, rôles, tokens, mémoire de la conversation | 30 min |
| 02 | [Régler la génération](modules/02-generation-settings/LESSON.md) | Température, streaming, hallucinations | 35 min |
| 03 | [Sorties structurées](modules/03-structured-output/LESSON.md) | Un objet typé plutôt que du texte libre | 35 min |
| | **Retrouver l'information** | | |
| 04 | [Embeddings](modules/04-embeddings/LESSON.md) | Texte en vecteur, similarité cosinus | 35 min |
| 05 | [Découper et chercher](modules/05-chunking-search/LESSON.md) | Passages par titres, recherche exhaustive | 45 min |
| 06 | [Base vectorielle](modules/06-vector-store/LESSON.md) | Index persistant, mise à jour, filtres | 35 min |
| | **RAG** | | |
| 07 | [Premier RAG](modules/07-first-rag/LESSON.md) | Réponse à partir des passages, avec citations | 35 min |
| 08 | [Évaluer](modules/08-evaluation/LESSON.md) | Jeu de questions, hit rate, MRR | 35 min |
| 09 | [Améliorer la recherche](modules/09-better-retrieval/LESSON.md) | Recherche hybride, décision par la mesure | 40 min |
| | **Livrer** | | |
| 10 | [Modèles hébergés](modules/10-hosted-models/LESSON.md) | OpenRouter, coût, latence, confidentialité | 35 min |
| 11 | [LangChain](modules/11-langchain/LESSON.md) | Le même RAG avec un framework | 40 min |
| 12 | [Outils et agents](modules/12-tools-agents/LESSON.md) | Le modèle décide quand chercher | 40 min |
| | **Entraîner** | | |
| 13 | [Entraîner un modèle](modules/13-training/LESSON.md) | Boucle d'entraînement, surapprentissage | 40 min |
| 14 | [Fine-tuning](modules/14-fine-tuning/LESSON.md) | LoRA sur un petit modèle de langage | 45 min |

Trois étapes demandent une préparation, rappelée en tête de leur leçon :

- avant le module 7, construire l'index complet : `uv run python -m assistant.store` (une à deux minutes sur
  un Mac récent, davantage sur un processeur seul) ;
- au module 10, une clé OpenRouter dans `.env` ;
- au module 11, `uv sync --group langchain`, et à partir du module 13, `uv sync --all-groups`.

## À deux

Tout le monde travaille sur la même branche. Tu ne modifies que ton dossier `learners/<ton prénom>/` : tes
copies d'exercices et ton `progress.md`. Personne ne touche aux fichiers de l'autre, donc `git pull` puis
`git push` passent sans conflit.

`progress.md` a une partie libre, « Notes ». Écris-y ce qui a coincé et tes questions ouvertes. Ces notes
servent à corriger les leçons : une difficulté rencontrée par l'un améliore le module pour tous.

Les clés d'API vivent dans `.env`, qui n'est jamais versionné.

## Faire évoluer le support

Le dépôt est fait pour grandir avec Claude Code. `CLAUDE.md` décrit le gabarit d'un module et la marche à
suivre. Les demandes prévues :

- « Ajoute un module sur le reclassement », ou tout autre sujet : un nouveau dossier au même gabarit, relié
  à l'assistant, ajouté au tableau ci-dessus.
- « Révise le module 6 » : le contenu est revérifié contre les versions actuelles des outils, les sorties
  citées sont rejouées, la date de vérification est mise à jour.
- « Tiens compte de nos notes de progression » : les leçons qui ont posé problème sont corrigées.

Chaque leçon affiche en tête la date de sa dernière vérification et les versions utilisées. Les chiffres et
les sorties qu'elle cite viennent d'exécutions réelles.

Pour rejouer la vérification de tout le support (chaque check doit échouer sur le squelette et passer sur la
référence, compter une dizaine de minutes) :

```shell
uv run --all-groups python -m course.selftest
```

## Organisation du dépôt

```
modules/NN-nom/    LESSON.md, exercise.py (squelette), check.py, DEEPER.md
assistant/         les briques de référence de l'assistant, une par module
course/            l'outillage des checks
data/golden.jsonl  les 52 questions d'évaluation
learners/          un dossier par apprenant
corpus/, .data/    documentation téléchargée, index et modèles affinés (hors git)
docs/              la conception et le plan d'origine du support
```

Le corpus est la documentation de Laravel 13 (licence MIT), figée à un commit précis et téléchargée au
premier besoin. Elle n'est pas redistribuée dans ce dépôt.
