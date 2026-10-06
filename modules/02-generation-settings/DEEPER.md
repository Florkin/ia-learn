# 02 · Pour aller plus loin

Exercices facultatifs, sans check.

## Mesurer le temps jusqu'au premier token

Chronomètre deux durées dans `stream_answer` : jusqu'au premier morceau, puis jusqu'au dernier. Compare une
question courte et une demande de texte long. Le premier chiffre est celui que ressent l'utilisateur.

## Changer de personnage sans changer de question

Pose la même question avec trois prompts système : un expert laconique, un formateur qui explique à un
débutant, un assistant qui répond uniquement par une liste à puces. Note ce que le prompt système contrôle
bien (ton, format) et ce qu'il contrôle mal (exactitude).

## Les autres réglages d'échantillonnage

`top_p` écarte les tokens les moins probables avant le tirage, `seed` fixe le générateur aléatoire. Passe
`seed=42` avec une température de 1.5 et vérifie que les réponses redeviennent identiques d'un appel à
l'autre.

## Chasser les hallucinations

Trouve trois autres questions sur Laravel 13 auxquelles le modèle répond faux, en cherchant dans les pages
`ai-sdk.md`, `images.md` ou `context.md` du corpus. Garde-les : elles serviront de questions témoins quand
l'assistant saura chercher dans la documentation.
