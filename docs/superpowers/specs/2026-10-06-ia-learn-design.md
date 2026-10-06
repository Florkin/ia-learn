# ia-learn : support de formation à l'IA engineering

Date : 2026-10-06. Statut : validé en conversation, implémenté le même jour. Les écarts décidés pendant
l'implémentation sont reportés ici.

## But

Apprendre à livrer des fonctionnalités d'IA dans une application (inférence, embeddings, base vectorielle,
RAG, évaluation, framework, outils), en comprenant assez le fonctionnement pour juger un choix technique,
avec des notions d'entraînement et de fine-tuning.

Le public est un développeur confirmé (PHP, TypeScript) qui lit le Python sans le pratiquer au quotidien et
part de presque zéro en IA. Deux personnes suivent le parcours, chacune sur sa machine. Une session dure
30 à 45 minutes.

Critère de réussite : à la fin du socle, l'apprenant a écrit lui-même chaque couche d'un assistant qui
répond à des questions sur une documentation, il sait le mesurer, et il sait dire quand un RAG, un modèle
hébergé, un framework ou un fine-tuning se justifie.

## Décisions prises

| Sujet | Décision | Raison |
|---|---|---|
| Format | Dépôt git cloné, leçons en markdown, exercices Python | Proche d'un vrai projet, s'étend par ajout de dossiers |
| Hébergement | Aucun serveur, le dépôt partagé suffit | La page du dépôt affiche déjà les leçons |
| Ordre | Chaque brique à la main, LangChain ensuite | On sait ce que le framework cache avant de s'en servir |
| Fil rouge | Un assistant de questions-réponses sur la documentation de Laravel 13 | Markdown propre, licence MIT, domaine connu des apprenants |
| Modèles | Ollama en local, OpenRouter au module 10 | Gratuit et observable d'abord, comparaison ensuite |
| Langue | Leçons en français, code et commentaires en anglais | Règle globale de Tristan |
| Fine-tuning | Deux variantes, MLX (Mac) et PyTorch avec PEFT (PC) | Le collègue n'a pas forcément un Mac |

## Outils et versions

Python 3.12 géré par uv, versions figées dans `uv.lock`. Vérifié le 2026-10-06 sur macOS (M5 Pro).

| Rôle | Outil | Note |
|---|---|---|
| Client des modèles | `openai` 3.x | Parle à Ollama et à OpenRouter, seule l'adresse change |
| Modèle de conversation local | `granite4.1:3b` (2,1 Go) | Français correct, JSON contraint et appel d'outils vérifiés |
| Modèle d'embeddings | `bge-m3` (1,2 Go, 1024 dimensions) | Multilingue : une question en français retrouve un passage en anglais |
| Base vectorielle | Chroma 1.5, embarquée | Aucune installation de serveur. pgvector en approfondissement |
| Framework | LangChain 1.4 (`langchain-openai`, `langchain-chroma`) | Module 11 seulement |
| Entraînement | PyTorch 2.14 | Modules 13 et 14 |
| Fine-tuning | `mlx-lm` sur Mac, `transformers` + `peft` sur PC | Module 14 |

Les dépendances lourdes sont dans des groupes uv (`langchain`, `training`) installés au moment où le module
en a besoin, pour que la première session démarre en quelques secondes.

## Structure du dépôt

```
ia-learn/
├── README.md              # carte du parcours, installation, déroulé d'une session
├── CLAUDE.md              # gabarit d'un module, procédures d'ajout et de révision
├── pyproject.toml, uv.lock, .python-version
├── .env.example           # prénom de l'apprenant, adresses et noms des modèles
├── assistant/             # le fil rouge : version de référence de chaque brique
├── course/                # outillage des checks (copie d'exercice, progression, erreurs lisibles)
├── modules/NN-slug/       # LESSON.md, exercise.py, check.py, DEEPER.md
├── data/golden.jsonl      # questions de référence pour l'évaluation
├── learners/<prénom>/     # copies d'exercices et progress.md de chaque personne
├── corpus/                # documentation Laravel, téléchargée, hors git
└── .data/                 # index vectoriels et modèles affinés, hors git
```

## Un module

| Fichier | Contenu |
|---|---|
| `LESSON.md` | En-tête (durée, prérequis, date de vérification), la notion en dix minutes de lecture, l'énoncé de l'exercice, ce qu'il faut retenir |
| `exercise.py` | Squelette avec une à trois fonctions à écrire. Son `__main__` fait tourner l'assistant dans l'état atteint à ce module |
| `check.py` | Vérifie les fonctions de l'apprenant et inscrit le module dans sa progression |
| `DEEPER.md` | Deux à quatre approfondissements facultatifs |

La solution d'un module est sa brique dans `assistant/`. Les modules suivants importent ces briques de
référence et jamais le code de l'apprenant, si bien qu'un exercice raté ou sauté ne bloque pas la suite.

### Déroulé d'une session

1. Lire `modules/04-embeddings/LESSON.md`.
2. Lancer `uv run modules/04-embeddings/check.py`. Au premier lancement, le check copie le squelette dans
   `learners/<prénom>/04-embeddings.py` et échoue en indiquant ce qui reste à écrire.
3. Compléter sa copie, la lancer pour voir le résultat (`uv run learners/<prénom>/04-embeddings.py`).
4. Relancer le check. Quand il passe, il ajoute une ligne datée dans `learners/<prénom>/progress.md`.

### Ce que vérifie un check

Les sorties d'un modèle varient d'un appel à l'autre. Un check teste donc d'abord ce qui est déterministe
(forme des messages, calculs, invariants d'un découpage, comportement face à un modèle simulé), puis fait
un ou deux appels réels avec des assertions larges (réponse non vide, JSON valide, source attendue parmi
les passages retrouvés). Un check qui échoue affiche en français ce qui était attendu et ce qui a été
obtenu. Si le modèle est injoignable, le message dit de lancer Ollama ou de vérifier `.env`.

## Parcours

| # | Dossier | Notion | Ce que l'apprenant écrit | Brique de référence |
|---|---|---|---|---|
| 1 | `01-first-call` | Messages, rôles, tokens, fenêtre de contexte, absence de mémoire | `build_messages`, `ask` | `assistant/llm.py` |
| 2 | `02-generation-settings` | Température, streaming, prompt système, pourquoi un modèle invente | `stream_answer`, `variants` | `assistant/llm.py` |
| 3 | `03-structured-output` | JSON contraint par un schéma, validation | `analyze_question` (langue, requête de recherche en anglais, hors sujet ou non) | `assistant/llm.py` |
| 4 | `04-embeddings` | Texte en vecteur, similarité cosinus | `embed`, `cosine_similarity`, `rank` | `assistant/embeddings.py` |
| 5 | `05-chunking-search` | Découpage par titres, recherche exhaustive | `chunk_markdown`, `search` | `assistant/chunking.py` |
| 6 | `06-vector-store` | Collection, identifiants, métadonnées, filtres, index approché | `build_index`, `query_index` | `assistant/store.py` |
| 7 | `07-first-rag` | Recherche puis génération, citations, savoir dire « je ne sais pas » | `build_prompt`, `answer` | `assistant/rag.py` |
| 8 | `08-evaluation` | Jeu de questions de référence, taux de succès, rang moyen | `first_relevant_rank`, `hit_rate`, `mrr`, `evaluate` | `assistant/evaluation.py` |
| 9 | `09-better-retrieval` | Recherche hybride (mots-clés et vecteurs), fusion des classements, reclassement | `reciprocal_rank_fusion`, `hybrid_search` | `assistant/retrieval.py` |
| 10 | `10-hosted-models` | Modèles hébergés, coût par token, latence, confidentialité | `cost`, `ask_target`, `compare` | `assistant/hosted.py` |
| 11 | `11-langchain` | Interfaces communes, composition, ce que le framework cache | `build_chain` | `assistant/rag_langchain.py` |
| 12 | `12-tools-agents` | Appel d'outils, boucle d'agent, garde-fous | `run_agent` | `assistant/agent.py` |
| 13 | `13-training` | Paramètres, perte, descente de gradient, époques, surapprentissage | `train` (boucle d'entraînement) | `assistant/classifier.py` |
| 14 | `14-fine-tuning` | LoRA, format des données, évaluation avant et après, quand affiner | `build_examples`, `split_examples` | `assistant/finetune.py` |

Les modules 13 et 14 traitent la même tâche de deux façons : prédire la section de la documentation d'où
vient un passage (Bases, Sécurité, Base de données, etc.). Le module 13 entraîne un petit classifieur sur
les embeddings, le module 14 affine un petit modèle de langage. La comparaison des deux résultats sert à
discuter quand un fine-tuning vaut son coût.

## Corpus

La documentation de Laravel 13, figée au commit `07b6889f` du dépôt `laravel/docs` (licence MIT). Un script
la télécharge dans `corpus/`, qui reste hors git. Le corpus retenu compte 76 pages : les sections
« Getting Started » à « Testing » du sommaire, sans le prologue ni les paquets optionnels. Le sommaire
fournit la section de chaque page, utilisée comme métadonnée de filtrage (module 6) et comme étiquette
(modules 13 et 14).

Les modules 4 à 6 travaillent sur un échantillon de sept pages courtes pour que les checks restent rapides sur
une machine sans carte graphique. L'index complet de référence est construit une fois, avant le module 7.

`data/golden.jsonl` contient 52 questions, majoritairement en français. Chacune donne la ou les pages où se
trouve la réponse et un terme que le bon passage doit contenir : juger à la page seule s'est révélé trop
indulgent pour départager deux méthodes de recherche. Une partie des questions cite des identifiants exacts
(noms de méthodes, clés de configuration) pour que la recherche par mots-clés du module 9 ait un effet
mesurable.

## Configuration

Un fichier `.env` à la racine, lu par `assistant/config.py`. Sans `.env`, tout pointe vers Ollama en local,
sauf le prénom qui est obligatoire.

| Variable | Défaut | Rôle |
|---|---|---|
| `LEARNER` | aucun | Nom du dossier dans `learners/` |
| `CHAT_BASE_URL`, `CHAT_API_KEY`, `CHAT_MODEL` | Ollama, `granite4.1:3b` | Modèle de conversation de tous les modules |
| `EMBED_BASE_URL`, `EMBED_API_KEY`, `EMBED_MODEL` | Ollama, `bge-m3` | Modèle d'embeddings |
| `OPENROUTER_API_KEY`, `HOSTED_MODELS` | vide, deux modèles bon marché et un modèle de pointe | Comparaison du module 10 |
| `FINETUNE_BACKEND` | `mlx` sur Mac Apple Silicon, `peft` ailleurs | Variante du module 14 |
| `FINETUNE_ITERS` | 200 | Longueur de l'entraînement du module 14, à réduire sur un processeur seul |

Une machine trop juste pour Ollama peut pointer `CHAT_*` et `EMBED_*` vers OpenRouter dès le module 1 :
`baai/bge-m3` y est disponible, donc les vecteurs restent comparables.

## Fine-tuning en deux variantes

La leçon, le jeu de données, le modèle de base et le check sont communs. Seul le moteur change.

| | Mac | PC |
|---|---|---|
| Moteur | `mlx-lm` | `transformers` + `peft` |
| Matériel | Apple Silicon | Carte NVIDIA, ou processeur seul |
| Sélection | `FINETUNE_BACKEND=mlx` | `FINETUNE_BACKEND=peft` |

Le modèle de base est `HuggingFaceTB/SmolLM2-360M-Instruct` (licence Apache 2.0, téléchargeable sans
compte). Mesuré à l'implémentation : 200 itérations prennent 34 secondes avec `mlx`, 113 secondes avec
`peft` sur la carte graphique d'un Mac et 7 minutes sur son processeur seul, pour 95 à 100 % de bonnes
réponses contre 7 % avant affinage. La variante `peft` tourne aussi sur
Mac, ce qui permet de comparer les deux sur la même machine. `assistant/finetune.py` expose deux fonctions,
`train` et `generate`, et délègue au moteur choisi.

## À deux

Tout le monde pousse sur la même branche. Chaque personne ne modifie que son dossier `learners/<prénom>/`,
donc les exercices et la progression ne créent pas de conflit. Le contenu commun (leçons, briques, checks)
évolue par des commits séparés.

`progress.md` contient les modules validés (lignes écrites par les checks) et une partie libre : ce qui a
coincé, les questions ouvertes. Une difficulté notée par l'un sert à corriger la leçon commune. Il n'existe
pas de version d'un module par personne.

## Évolution

`CLAUDE.md` à la racine porte les règles que Claude applique quand on lui demande de faire évoluer le
support.

| Demande | Effet |
|---|---|
| « Ajoute un module sur X » | Nouveau dossier au gabarit, brique dans `assistant/` si le fil rouge est concerné, ligne dans la carte du README |
| « Révise le module N » | Contenu revérifié contre la documentation actuelle des outils, exercice et check relancés, date de vérification mise à jour |
| « Tiens compte de ma progression » | Lecture des `progress.md`, corrections dans les leçons qui ont posé problème, proposition de modules suivants |
| Approfondir un sujet | Les `DEEPER.md` proposent des exercices de second passage, sans check obligatoire |

Chaque leçon affiche en tête la date de sa dernière vérification et les versions d'outils concernées.

## Vérification du support

Chaque module est livré après deux contrôles exécutés réellement sur la machine de Tristan : le check échoue
sur le squelette non complété, et il passe quand on lui donne la solution de référence. Un script
`course/selftest.py` rejoue ces deux contrôles pour tous les modules, pour valider une révision.

Le module 10 n'a pas pu être vérifié contre OpenRouter, faute de clé d'API. Son code est vérifié contre
l'adresse locale, qui suit le même protocole, et contre la liste de prix publique d'OpenRouter. Le moteur
`peft` du module 14 n'a été exécuté que sur un Mac.

## Hors périmètre

- Site web, comptes, exécution de code dans le navigateur.
- Modèles servis par un serveur partagé.
- Déploiement de l'assistant en production, interface graphique.
- Théorie détaillée des transformers (mécanisme d'attention), génération d'images, audio.
- Agents à plusieurs outils et orchestration avancée : candidats pour des modules ajoutés plus tard.
