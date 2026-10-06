# 12 · Outils et agents

> Durée : 40 min. Prérequis : modules 07 et 09.
> Vérifié le 2026-10-06 avec Ollama 0.21, `granite4.1:3b` et `openai` 3.24.

## Objectif

Laisser le modèle décider lui-même quand chercher dans la documentation, en écrivant la boucle qui exécute
ses demandes, et savoir quand cette liberté vaut son prix.

## La notion

### Du pipeline à l'agent

L'assistant du module 7 suit un chemin fixe : chercher, puis répondre. Il cherche même quand on lui dit
bonjour, et une seule fois même quand la question en contient deux.

Un agent renverse la décision. On décrit au modèle les outils dont il dispose, et il choisit à chaque étape
entre répondre et demander l'exécution d'un outil.

### L'appel d'outil

Le modèle n'exécute jamais rien. Il écrit une demande, et ton code décide de l'honorer. L'échange se fait en
quatre temps.

1. Tu envoies la conversation avec la liste des outils. Chaque outil a un nom, une description et le schéma
   JSON de ses arguments (constante `TOOLS` de `assistant/agent.py`).
2. Le modèle répond soit par du texte, soit par une demande :

```json
{"role": "assistant", "content": "",
 "tool_calls": [{"id": "call_z92pc2a1", "type": "function",
                 "function": {"name": "search_docs",
                              "arguments": "{\"query\":\"how to hash a password in Laravel\"}"}}]}
```

3. Ton code exécute la fonction correspondante et ajoute le résultat à la conversation, dans un message de
   rôle `tool` qui reprend l'identifiant de la demande.
4. Tu rappelles le modèle avec la conversation complétée. Il répond, ou demande un autre outil.

Remarque la demande ci-dessus : la question était en français, et le modèle a formulé de lui-même une
requête en anglais adaptée à la documentation. C'est la réécriture du module 9, obtenue sans l'écrire.

### Un agent est une boucle

```
messages = [consignes, question]
répéter au plus max_steps fois :
    message = modèle(messages, outils)
    si le message ne demande aucun outil : c'est la réponse, on s'arrête
    sinon : exécuter chaque outil demandé, ajouter les résultats aux messages
```

Tout ce qu'on appelle agent, y compris dans les frameworks, est cette boucle : un modèle, des outils, une
condition d'arrêt.

### Ce qu'on gagne

L'assistant ne cherche plus pour un bonjour. Il reformule ses requêtes, et peut chercher plusieurs fois
quand la première recherche ne suffit pas. Avec d'autres outils, il pourrait choisir entre plusieurs
sources.

### Ce qu'on perd

La décision de chercher appartient maintenant au modèle, et il peut mal décider. Avec une consigne polie
(« pour toute question sur Laravel, appelle d'abord l'outil de recherche »), le modèle local a sauté la
recherche pour deux questions Laravel sur cinq lors de la préparation de ce module. À la question témoin du
module 2, il a répondu de mémoire `php artisan ai:agent create`, une commande qui n'existe pas.
L'hallucination que le RAG avait supprimée est revenue.

Le prompt de l'exercice est plus ferme : il affirme que les connaissances du modèle sont périmées et que
l'outil est obligatoire. Avec lui, les cinq questions déclenchent une recherche. Deux formulations d'une
même consigne donnent deux comportements, et seule une mesure dit laquelle tient.

S'y ajoutent le coût, puisque chaque question demande au moins deux appels au modèle, et la difficulté à
tester un système dont le chemin change selon la question.

### Les garde-fous

- **Un nombre d'étapes maximal.** Un modèle peut redemander le même outil sans fin.
- **Une liste fermée d'outils.** On n'exécute que les fonctions déclarées (`TOOL_FUNCTIONS`). Le nom demandé
  par le modèle ne sert jamais à appeler une fonction arbitraire.
- **Des arguments traités comme une saisie utilisateur.** Le modèle peut envoyer un JSON invalide ou un
  argument inattendu. `call_tool` renvoie alors un texte d'erreur au modèle au lieu de planter.
- **Une validation humaine pour ce qui agit.** `search_docs` ne fait que lire. Un outil qui envoie un
  e-mail, modifie une base ou dépense de l'argent ne doit pas partir sur la seule décision du modèle,
  d'autant qu'un passage retrouvé peut contenir des instructions hostiles (module 7).

### Pipeline ou agent

Quand les étapes sont connues d'avance, le pipeline est le bon choix : il est prévisible, moins cher et
facile à mesurer. Un agent se justifie quand le chemin dépend vraiment de la question, par exemple pour
choisir entre plusieurs sources ou enchaîner des recherches. On commence par le pipeline, et on ne passe à
l'agent que pour ce qu'il ne sait pas faire.

### Côté Python

`run_agent` reçoit la fonction `complete` en paramètre, avec le vrai appel au modèle comme valeur par
défaut. Le check lui passe à la place un faux modèle qui rejoue des messages préparés. C'est ce qui permet
de tester la boucle sans dépendre des humeurs d'un vrai modèle.

## L'exercice

1. Lance `uv run modules/12-tools-agents/check.py` pour créer ta copie.
2. Écris `run_agent` en suivant les étapes de sa docstring. L'outil, le prompt et l'appel au modèle sont
   fournis par `assistant/agent.py`, que tu peux lire.
3. Lance ta copie. Dis bonjour, pose une question sur Laravel, puis une question en deux parties. Regarde
   les lignes `[outil]` : combien de recherches, avec quelles requêtes.
4. Pose la question témoin du module 2 sur le AI SDK et vérifie que l'agent cherche avant de répondre.
5. Relance le check jusqu'à ce qu'il passe. Quatre de ses étapes utilisent un faux modèle.

## À retenir

- Le modèle demande un outil, ton code l'exécute et lui renvoie le résultat.
- Un agent est une boucle : modèle, outils, condition d'arrêt.
- Laisser le modèle décider apporte de la souplesse et retire de la prévisibilité.
- Nombre d'étapes borné, outils en liste fermée, arguments validés, validation humaine pour toute action.
- Pipeline par défaut, agent quand le chemin dépend de la question.

## Dans l'assistant

L'assistant a maintenant deux modes : le pipeline `answer` du module 7, qui cherche toujours, et l'agent
`run_agent`, qui décide. Le socle du parcours garde le premier comme référence.
