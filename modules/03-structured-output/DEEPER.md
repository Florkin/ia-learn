# 03 · Pour aller plus loin

Exercices facultatifs, sans check.

## Le raccourci du paquet `openai`

`client.chat.completions.parse(..., response_format=QuestionAnalysis)` fait les deux étapes à ta place :
le schéma est tiré de la classe, et l'objet validé est dans `response.choices[0].message.parsed`. Réécris
`analyze_question` avec ce raccourci et compare la longueur du code.

## Extraire un ticket de support

Écris une classe `Ticket` (titre, priorité parmi trois valeurs, liste de plateformes touchées, résumé d'une
phrase) et une fonction qui l'extrait d'un message comme « Le paiement plante sur mobile depuis ce matin,
c'est urgent, ça touche iOS et Android ». Teste avec un message vague, puis avec un message qui ne décrit
aucun problème. Décide ce que la fonction doit renvoyer dans ce dernier cas.

## Mesurer le champ `about_laravel`

Écris vingt questions avec la réponse attendue, dont cinq qui citent une méthode ou une classe de Laravel
sans dire le mot « Laravel ». Calcule le taux de bonnes réponses. Ajoute ensuite deux ou trois exemples
résolus dans le prompt système et mesure à nouveau. Tu viens de faire une évaluation, sujet du module 8.

## Valider au-delà du schéma

Un schéma ne sait pas dire « la requête de recherche doit être en anglais ». Ajoute un validateur Pydantic
(`@field_validator`) qui refuse une requête contenant des caractères accentués, et relance l'appel une fois
quand la validation échoue.
