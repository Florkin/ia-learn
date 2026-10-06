# ia-learn : consignes pour Claude

Support de formation à l'IA engineering, suivi par deux développeurs. Un assistant de questions-réponses sur
la documentation de Laravel sert de fil rouge. La conception d'origine est dans
`docs/superpowers/specs/2026-10-06-ia-learn-design.md`.

## Règles du dépôt

- Leçons, README et messages affichés à l'apprenant en français, tutoiement. Code, identifiants, noms de
  fichiers, commentaires et docstrings en anglais.
- Tout fichier se lit et s'écrit avec `encoding="utf-8"` explicite (un des apprenants peut être sous
  Windows).
- `.env`, `corpus/` et `.data/` ne sont jamais versionnés.
- Une leçon ne cite que des chiffres et des sorties obtenus par une exécution réelle. Ce qui n'a pas pu être
  exécuté est signalé comme tel dans l'en-tête de la leçon.
- La brique de référence d'un module (`assistant/`) expose les mêmes noms de fonctions que son exercice.
  C'est ce qui permet au check de tourner sur l'une ou sur l'autre.
- Un check et une brique n'importent jamais le code d'un apprenant. Les modules s'appuient sur `assistant/`.
- On ne crée pas de version d'un module par apprenant. Une difficulté notée dans un `progress.md` corrige la
  leçon commune.
- Les dépendances lourdes vont dans un groupe uv (`langchain`, `training`), et le check commence par
  `require(...)` pour afficher la commande d'installation.

## Gabarit d'un module

`modules/NN-slug/` contient quatre fichiers.

**`LESSON.md`**, dix minutes de lecture :

```
# NN · Titre

> Durée : 35 min. Prérequis : module NN.
> Vérifié le AAAA-MM-JJ avec <outils et versions>.

## Objectif          une ou deux phrases
## La notion         sous-parties en ###, avec les sorties réelles, et « Côté Python » si une tournure le demande
## L'exercice        étapes numérotées, la première lance le check
## À retenir         quatre à cinq puces
## Dans l'assistant  ce que la brique devient dans le fil rouge
```

**`exercise.py`** : le squelette. Une à trois fonctions qui lèvent `NotImplementedError`, avec une docstring
qui donne les étapes et les appels utiles. Ce qui n'est pas le sujet du module est importé de `assistant/`.
Le bloc `__main__` fait tourner l'assistant dans l'état atteint.

**`check.py`** : `check = Check(__file__, reference="assistant.<brique>")`, puis des étapes
`with check.step("..."):` et `check.finish()`. Les étapes déterministes passent en premier (calculs, forme
des données, faux modèle), les appels réels ensuite avec des assertions larges. Chaque assertion porte un
message en français qui dit ce qui était attendu et ce qui a été obtenu.

**`DEEPER.md`** : trois à cinq approfondissements facultatifs, sans check, chacun terminé par une
observation ou une mesure à faire.

Style des textes : phrases directes, pas de tiret cadratin, titres avec une seule majuscule, pas de formule
de conclusion. Un terme technique anglais consacré reste en anglais (RAG, embedding, prompt, token).

## Ajouter un module

1. Choisir le numéro suivant et un slug anglais. Décider ce que l'apprenant écrit (une à trois fonctions) et
   ce qui est fourni.
2. Écrire `check.py` et `exercise.py`. Constater l'échec :
   `COURSE_MODE=skeleton uv run modules/NN-slug/check.py` sort en code 1 sur une étape, sans trace Python.
3. Écrire la brique dans `assistant/`. Constater le succès :
   `COURSE_MODE=reference uv run modules/NN-slug/check.py` sort en code 0, trois fois de suite si le check
   appelle un modèle.
4. Lancer la démonstration du module et garder ses sorties.
5. Écrire `LESSON.md` et `DEEPER.md` à partir de ces sorties.
6. Ajouter la ligne au tableau du README. Lancer `uv run --all-groups python -m course.selftest`.
7. Un commit pour le module.

## Réviser un module

1. Relire l'en-tête : date et versions de la dernière vérification.
2. Vérifier les outils contre leur documentation actuelle (noms de modèles, paramètres d'API, options de
   bibliothèques). Mettre à jour `pyproject.toml` et `uv.lock` si une version change.
3. Rejouer le check dans les deux modes et la démonstration. Remplacer dans la leçon toute sortie ou tout
   chiffre qui a changé.
4. Mettre à jour la ligne « Vérifié le ». Si le changement touche une brique utilisée plus loin, rejouer le
   selftest complet.

## Tenir compte de la progression

Lire `learners/*/progress.md`. Les lignes « validé le » donnent l'avancement, la partie « Notes » ce qui a
coincé. Pour chaque difficulté, corriger la leçon ou le message du check concerné, puis le dire à
l'apprenant. Proposer les modules suivants selon ce que les notes demandent.

## Commandes

```shell
uv run modules/NN-slug/check.py                      # as a learner (needs LEARNER in .env)
COURSE_MODE=skeleton uv run modules/NN-slug/check.py   # must fail
COURSE_MODE=reference uv run modules/NN-slug/check.py  # must pass
uv run --all-groups python -m course.selftest [NN]   # both, for every module or the given prefixes
uv run python -m assistant.store                     # build the reference index
```

## État des vérifications

Vérifié le 2026-10-06 sur un Mac M5 Pro : les quatorze modules, dans les deux modes.

Reste à vérifier dès que le moyen existe, puis à reporter dans l'en-tête des leçons concernées :

- module 10 : les appels réels à OpenRouter (aucune clé n'était disponible) ;
- module 14 : le moteur `peft` sous Windows, sous Linux et sur une carte NVIDIA ;
- l'ensemble du parcours sur une machine sans carte graphique, pour confirmer les durées annoncées.

## Pistes de modules

Reclassement avec un modèle dédié, évaluation des réponses par un modèle juge, pgvector, ingestion de PDF et
de pages web, agents à plusieurs outils et LangGraph, MCP, mise en cache des prompts, exposition de
l'assistant par une API avec streaming, modèles multimodaux.
