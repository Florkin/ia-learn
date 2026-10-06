# 12 · Pour aller plus loin

Exercices facultatifs, sans check.

## Mesurer la décision de chercher

Fais passer les 52 questions de `data/golden.jsonl` à l'agent et compte celles pour lesquelles il n'a lancé
aucune recherche. Toutes concernent Laravel, donc chaque absence est une faute. Compare le prompt de
l'exercice à une version plus courte de ta main. Tu obtiens un taux d'appel d'outil, la première mesure à
suivre sur un agent.

## Un second outil

Ajoute un outil `search_exact(identifier)` qui s'appuie sur `keyword_search` du module 9, avec une
description qui dit quand s'en servir (noms de méthodes, variables d'environnement, options de commande).
Pose des questions des deux sortes et note quel outil le modèle choisit. La description de l'outil fait
partie du prompt : reformule-la et observe l'effet.

## Les questions en plusieurs parties

« Quelle est la différence entre `Cache::put` et `Cache::forever`, et comment vider tout le cache ? » :
l'agent de référence ne lance qu'une recherche et répond de façon incomplète à la seconde moitié. Modifie le
prompt pour qu'il découpe la question et cherche chaque partie, puis vérifie sur cinq questions doubles.

## La même boucle avec LangChain

`from langchain.agents import create_agent` construit un agent à partir d'un modèle et d'une liste de
fonctions Python. Reconstruis l'agent de ce module en quelques lignes, puis retrouve dans ton `run_agent`
chacune des choses que le framework fait à ta place : la boucle, le schéma des outils déduit de la
fonction, l'exécution, la limite d'étapes.
