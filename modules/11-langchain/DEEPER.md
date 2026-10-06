# 11 · Pour aller plus loin

Exercices facultatifs, sans check.

## Renvoyer aussi les sources

La chaîne de l'exercice rend une chaîne de caractères et perd les passages en route. Modifie-la pour qu'elle
rende un dictionnaire `{"answer": ..., "sources": [...]}`, à l'aide de `RunnablePassthrough.assign` ou de
`RunnableParallel`. Compare l'effort à celui du module 7, où `answer` renvoyait les deux d'emblée.

## Changer une pièce

Remplace `ChatOpenAI` par un modèle hébergé d'OpenRouter en ne touchant qu'à sa création. Puis traite trois
questions d'un coup avec `chain.batch([...])` et mesure le temps total par rapport à trois `invoke`
successifs.

## Le découpage de LangChain contre le tien

Installe `langchain-text-splitters` (`uv add --group langchain langchain-text-splitters`) et découpe la page
`routing.md` avec `MarkdownHeaderTextSplitter`. Compare ses passages aux tiens : chemin des titres, sort du
sommaire et des ancres, lignes `#` dans les blocs de code.

## Regarder ce qui part vraiment

Ajoute `import langchain; langchain.debug = True` avant d'appeler la chaîne, ou insère dans la chaîne une
étape `RunnableLambda(lambda x: print(x) or x)` après le prompt. Vérifie que les messages envoyés au modèle
sont bien ceux de ton `build_prompt`.
