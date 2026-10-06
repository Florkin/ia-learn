# 01 · Pour aller plus loin

Exercices facultatifs, sans check. À faire dans ta copie ou dans un fichier à part.

## Voir l'historique grossir

Dans la boucle de discussion, affiche après chaque tour `response.usage.prompt_tokens` et
`response.usage.completion_tokens`. Il faut pour cela que `ask` renvoie aussi l'objet `usage`. Observe la
progression du nombre de tokens en entrée sur dix tours.

## Borner la mémoire

Limite l'historique aux six derniers messages avant de l'envoyer. Cherche la question qui met ce choix en
défaut, puis une stratégie qui y résiste : garder le premier message, ou demander au modèle de résumer les
tours anciens en un seul message.

## Se passer du paquet `openai`

Réécris `ask` avec `urllib.request` et `json` de la bibliothèque standard. Tu verras ce que le paquet fait
pour toi : sérialisation, en-têtes, relances sur erreur réseau, objets typés.

## La fenêtre de contexte coûte de la mémoire

Pendant qu'un modèle est chargé, `ollama ps` affiche sa colonne `CONTEXT`. Ollama choisit cette taille selon
la mémoire disponible. Sur une machine de 64 Go il réserve les 131 072 tokens de `granite4.1:3b`, soit
21 Go de mémoire pour un modèle de 2 Go. Relance le serveur avec `OLLAMA_CONTEXT_LENGTH=8192 ollama serve`
et compare la colonne `SIZE`.
