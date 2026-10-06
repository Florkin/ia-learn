# 03 · Sorties structurées

> Durée : 35 min. Prérequis : module 01.
> Vérifié le 2026-10-06 avec Ollama 0.21, `granite4.1:3b`, `openai` 3.24 et `pydantic` 2.13.

## Objectif

Obtenir du modèle un objet typé que ton code peut utiliser sans analyser de texte libre.

## La notion

### Le code a besoin de données

Une application ne sait rien faire d'une phrase. Pour ranger un ticket, remplir un formulaire ou choisir un
traitement, il lui faut des champs. Demande au modèle d'analyser une question, sans préciser de format :

```
Language: fr
About Laravel: No
Short Search Query: joke
```

L'information est là, mais sous une forme qui change d'un appel à l'autre. Sur douze questions posées ainsi,
aucune réponse n'était lisible par un programme.

### Contraindre la sortie par un schéma

L'API accepte un schéma JSON dans le paramètre `response_format`. Le serveur s'en sert pendant la
génération : à chaque token, il écarte ceux qui feraient sortir la réponse du schéma. Le résultat est
toujours un JSON valide, avec les bons champs et les bons types.

```json
{"language": "fr", "about_laravel": true, "search_query": "how to cache query result for ten minutes in laravel"}
```

### Décrire le schéma avec Pydantic

Écrire un schéma JSON à la main est pénible. Pydantic le déduit d'une classe, puis valide la réponse et la
transforme en objet. C'est l'équivalent d'un DTO validé avec le Validator de Symfony, ou d'un schéma zod.

```python
class QuestionAnalysis(BaseModel):
    language: Literal["fr", "en"]   # an enum of two values
    about_laravel: bool

QuestionAnalysis.model_json_schema()          # the JSON schema, as a dict
QuestionAnalysis.model_validate_json(text)    # an object, or a ValidationError
```

### Le schéma fixe la forme, le prompt donne le sens

La contrainte garantit qu'un champ `about_laravel` existe et contient un booléen. Elle ne dit pas au modèle
ce que ce champ signifie. Avec Ollama, le modèle ne voit que le prompt : le prompt système de l'exercice
décrit donc chaque champ en une ligne. Un schéma sans explication donne des objets valides et des valeurs
au hasard.

### Une forme valide n'est pas une réponse juste

```
À quoi sert whereBelongsTo ?
  QuestionAnalysis(language='fr', about_laravel=False, search_query='what is whereBelongsTo')
```

`whereBelongsTo` est une méthode d'Eloquent. Le modèle ne la connaît pas et classe la question hors sujet,
dans un objet irréprochable sur la forme. Deux leçons pratiques en sortent. Un champ produit par un modèle se
mesure sur des exemples avant de servir à une décision. Et tant qu'il n'est pas mesuré, on évite de s'en
servir comme barrière : si l'assistant refusait toute question jugée hors sujet, il refuserait celle-ci.

### À quoi ça sert

Cette technique est derrière la plupart des fonctionnalités d'IA livrées en entreprise : extraire les champs
d'un e-mail ou d'une facture, classer une demande, router vers le bon traitement. Dans l'assistant, elle
produit une requête de recherche en anglais à partir d'une question en français, ce qui comptera au module 9
puisque la documentation est en anglais.

## L'exercice

1. Lance `uv run modules/03-structured-output/check.py` pour créer ta copie.
2. Ajoute à `QuestionAnalysis` le troisième champ décrit dans `ANALYSIS_PROMPT`.
3. Écris `analyze_question` : appel au modèle avec `response_format`, puis validation de la réponse.
4. Lance ta copie et lis les quatre objets produits. Repère celui qui est faux.
5. Retire temporairement `response_format` de l'appel et relance. Selon le prompt, le modèle répond encore en
   JSON ou non : rien ne le garantit plus.
6. Relance le check jusqu'à ce qu'il passe.

## À retenir

- `response_format` avec un schéma JSON garantit la forme de la réponse.
- Pydantic génère le schéma et valide la réponse en un objet typé.
- Le sens de chaque champ s'explique dans le prompt.
- Une réponse valide peut être fausse. Ce qu'on en fait dépend de ce qu'on a mesuré.

## Dans l'assistant

`analyze_question` donne à l'assistant la langue de la question et une requête de recherche en anglais. Le
champ `about_laravel` reste informatif tant qu'il n'a pas été évalué.
