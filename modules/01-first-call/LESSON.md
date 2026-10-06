# 01 · Premier appel à un modèle

> Durée : 30 min. Prérequis : l'installation décrite dans le README.
> Vérifié le 2026-10-06 avec Ollama 0.21, `granite4.1:3b` et `openai` 3.24.

## Objectif

Envoyer une conversation à un modèle de langage depuis du code, lire sa réponse, et comprendre pourquoi il
faut lui renvoyer tout l'historique à chaque appel.

## La notion

### Un modèle est un service HTTP

Vu depuis une application, un modèle de langage est une API : on poste du JSON, on reçoit du JSON. Ollama
en expose une sur ta machine, à l'adresse `http://localhost:11434/v1`. Tu peux l'appeler sans une ligne de
Python.

```shell
curl -s http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "granite4.1:3b",
  "temperature": 0,
  "messages": [
    {"role": "system", "content": "You are a concise assistant. Answer in the language of the question."},
    {"role": "user", "content": "En une phrase, à quoi sert une route dans un framework web ?"}
  ]
}'
```

La réponse, raccourcie :

```json
{
  "model": "granite4.1:3b",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Dans un framework web, une route permet de mapper les demandes HTTP aux contrôleurs ou fonctions spécifiques pour gérer les réponses appropriées en fonction des URL demandées."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 42, "completion_tokens": 40, "total_tokens": 82}
}
```

Ce format a été défini par OpenAI et presque tous les fournisseurs l'ont repris. C'est ce qui permettra, au
module 10, de passer d'Ollama à un modèle hébergé en changeant une adresse et une clé.

### Messages et rôles

On n'envoie pas une question isolée, on envoie une liste de messages. Chacun a un rôle.

- `system` donne les consignes permanentes : le ton, la langue, ce que l'assistant doit refuser. L'utilisateur
  final ne le voit pas.
- `user` porte ce que dit l'utilisateur.
- `assistant` porte ce que le modèle a répondu aux tours précédents.

Le modèle lit la liste entière et produit le message `assistant` suivant.

### Le modèle n'a pas de mémoire

Chaque appel est indépendant. Deux appels successifs, sans historique :

```
> My name is Ada.
Your name is Ada.
> What is my name?
Your name is not provided in your question.
```

Une interface de discussion donne l'impression d'une mémoire parce qu'elle renvoie toute la conversation à
chaque tour. La mémoire est donc à ta charge : tu stockes les messages et tu décides lesquels repartent.

### Tokens et fenêtre de contexte

Un modèle ne lit pas des caractères mais des tokens, des morceaux de mots. Compte environ quatre tokens pour
trois mots en anglais, un peu plus en français. Le bloc `usage` de la réponse donne le compte exact :
42 tokens en entrée pour deux messages courts, 40 en sortie.

Ce compte a deux conséquences pratiques. Les modèles hébergés facturent au token, entrée et sortie
séparément. Et chaque modèle a une fenêtre de contexte, le nombre maximal de tokens qu'il peut lire en un
appel, historique compris. `granite4.1:3b` accepte 131 072 tokens. Au-delà, Ollama coupe le début de
la conversation sans message d'erreur, et une API hébergée refuse la requête.

Comme l'historique repart à chaque tour, le nombre de tokens en entrée grandit à chaque échange. Une
conversation longue coûte de plus en plus cher par message, et finit par déborder.

`finish_reason` dit pourquoi le modèle s'est arrêté : `stop` quand il a fini, `length` quand il a atteint
une limite de longueur.

### Côté Python

Le paquet `openai` construit la requête HTTP et transforme la réponse en objet. Deux tournures du squelette
méritent un mot si tu viens de PHP ou de TypeScript.

- `[premier, *history, dernier]` déplie une liste dans une autre, comme `...history`.
- `list[dict] | None` est une annotation de type, sans effet à l'exécution.

## L'exercice

1. Lance `uv run modules/01-first-call/check.py`. Il crée ta copie de l'exercice dans
   `learners/<ton prénom>/01-first-call.py` et échoue, c'est attendu.
2. Écris `build_messages` : le message système, puis l'historique, puis la question.
3. Écris `ask` : appelle `client.chat.completions.create(...)` avec ces messages et renvoie le texte de la
   réponse, qui se trouve dans `response.choices[0].message.content`.
4. Lance ta copie (`uv run learners/<ton prénom>/01-first-call.py`) et discute. Donne ton prénom, puis
   demande-le au tour suivant.
5. Mets en commentaire la ligne `history += ...` à la fin du fichier et refais l'essai. Le modèle a oublié.
   Rétablis la ligne.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- Un appel à un modèle est une requête HTTP qui porte une liste de messages.
- Trois rôles : `system` pour les consignes, `user` et `assistant` pour les tours de parole.
- Le modèle ne retient rien entre deux appels. L'historique est stocké et renvoyé par ton application.
- Tout se compte en tokens : la facture, et la limite de ce que le modèle peut lire.

## Dans l'assistant

`ask` est la première brique de l'assistant. Sa version de référence est dans `assistant/llm.py`, et tous les
modules suivants passent par elle pour parler au modèle.
