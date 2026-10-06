# 10 · Pour aller plus loin

Exercices facultatifs, sans check. Ils consomment un peu de crédit OpenRouter.

## Le coût réel contre le coût calculé

OpenRouter renvoie le montant facturé dans le bloc `usage` de la réponse. Affiche `response.usage` en entier
pour un appel et compare ce montant à celui de ta fonction `cost`. Un écart vient en général du compte des
tokens, qui diffère d'un fournisseur à l'autre pour le même texte.

## Faire passer l'évaluation à un autre modèle

Le module 9 montrait que la réécriture de la question par le modèle local coûte une demi-seconde. Mets un
modèle hébergé bon marché dans `CHAT_MODEL` et relance l'exercice du module 9. Compare le tableau obtenu et
la durée totale. Remets ensuite ta configuration locale.

## Un juge plus fort

Reprends l'approfondissement « Un modèle comme juge » du module 8 avec le modèle de pointe comme juge des
réponses du modèle local. Sur vingt questions, compte les réponses qu'il déclare infidèles aux passages et
vérifie-en cinq à la main.

## Tout faire tourner sans Ollama

Dans un `.env` de test, pointe `CHAT_*` et `EMBED_*` vers OpenRouter avec `baai/bge-m3` comme modèle
d'embeddings. Les vecteurs viennent du même modèle que l'index local, donc l'index reste valable en
principe. Vérifie-le en relançant l'évaluation du module 8 : si les chiffres bougent, les deux versions du
modèle ne produisent pas exactement les mêmes vecteurs et il faut réindexer.
