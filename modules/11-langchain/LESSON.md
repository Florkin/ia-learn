# 11 · LangChain

> Durée : 40 min. Prérequis : module 07. Installation : `uv sync --group langchain`.
> Vérifié le 2026-10-06 avec `langchain` 1.4, `langchain-openai` 1.6 et `langchain-chroma` 1.1.

## Objectif

Reconstruire le RAG du module 7 avec LangChain, vérifier qu'il se comporte comme le tien, et savoir dire ce
que le framework apporte et ce qu'il coûte.

## La notion

### Ce qu'est LangChain

LangChain est une bibliothèque qui donne une interface commune aux pièces que tu as écrites à la main, et
une façon de les enchaîner. Chaque pièce existe en dizaines de variantes interchangeables : un modèle de
conversation chez n'importe quel fournisseur, une base vectorielle parmi une cinquantaine, des lecteurs de
PDF, de pages web ou de Notion.

Tu connais déjà tout ce qu'il y a dessous. La correspondance avec ton code :

```
ton code (modules 1 à 7)              LangChain
embed()                               OpenAIEmbeddings
open_collection() + query_index()     Chroma(...).as_retriever()
Chunk                                 Document (page_content, metadata)
build_prompt()                        ChatPromptTemplate + format_docs
chat()                                ChatOpenAI + StrOutputParser
answer()                              la chaîne assemblée
```

### Assembler avec `|`

LangChain enchaîne les pièces avec l'opérateur `|`, comme un tube Unix. La sortie de chaque étape devient
l'entrée de la suivante :

```python
chain = (
    {"passages": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
chain.invoke("Comment hacher un mot de passe ?")
```

Le dictionnaire du début lance ses deux branches sur la même entrée, la question. La branche `passages`
cherche puis met en forme. La branche `question` laisse passer la question telle quelle. Le résultat, un
dictionnaire à deux clés, remplit les deux variables du prompt.

### Ce que le framework apporte

- **L'interchangeabilité.** Remplacer Chroma par pgvector ou Ollama par un autre fournisseur change une
  ligne, celle qui crée la pièce.
- **Des comportements gratuits.** Toute chaîne sait répondre d'un bloc (`invoke`), au fil de l'eau
  (`stream`), par lots (`batch`) et en asynchrone, sans code de ta part. Au module 2 tu avais écrit le
  streaming à la main.
- **Un écosystème.** Lecteurs de documents, outils de traçage des appels, et un vocabulaire que beaucoup
  d'équipes partagent.

### Ce qu'il coûte

- **Des choix par défaut que tu n'as pas faits.** Sans l'option `check_embedding_ctx_length=False`,
  `OpenAIEmbeddings` découpe le texte avec le tokenizer d'OpenAI et envoie des numéros de tokens. Ollama
  répond `400 invalid input type`. Rien dans le message ne mène à la cause. Tu la trouves parce que tu sais,
  depuis le module 4, ce qu'un appel d'embeddings doit contenir.
- **Des couches à traverser.** Une erreur remonte à travers une dizaine de fichiers du framework avant
  d'atteindre ton code. Le RAG de référence fait 36 lignes dans `assistant/rag.py`, que tu peux lire d'un
  trait.
- **Du poids et du mouvement.** Le groupe `langchain` fait passer le projet de 88 à 108 paquets. La
  bibliothèque a changé plusieurs fois de façon de faire, si bien que beaucoup de tutoriels en ligne ne
  fonctionnent plus tels quels.
- **Les limites de l'abstraction.** Dès que tu sors du cas prévu (la recherche hybride du module 9 avec
  réécriture de la question, ton évaluation), tu écris de nouveau ton propre code, cette fois dans les
  conventions du framework.

### Quand s'en servir

LangChain rend service quand il faut brancher beaucoup de sources ou de fournisseurs différents, quand une
équipe s'en sert déjà, ou pour orchestrer des agents à plusieurs étapes (sa bibliothèque sœur LangGraph).
Pour un RAG sur un corpus, le code direct est plus court, plus lisible et plus stable. Dans les deux cas, tu
es maintenant capable de lire ce que le framework fait à ta place, ce qui est la condition pour s'en servir
sans le subir.

### Côté Python

`a | b` n'a rien de magique : les objets LangChain redéfinissent l'opérateur (méthode `__or__`) pour
construire une séquence. Un dictionnaire placé dans une chaîne est converti en étape qui exécute chaque
valeur.

## L'exercice

1. Installe le groupe : `uv sync --group langchain`.
2. Lance `uv run modules/11-langchain/check.py` pour créer ta copie.
3. Écris `format_docs`, l'équivalent de la mise en forme des passages du module 7.
4. Écris `build_retriever`. Il ouvre l'index que tu as déjà construit, sans rien réindexer.
5. Écris `build_chain` en assemblant les pièces avec `|`.
6. Lance ta copie et pose les mêmes questions qu'au module 7. Les réponses arrivent au fil de l'eau.
7. Retire `check_embedding_ctx_length=False`, relance, lis l'erreur, puis remets l'option.
8. Relance le check jusqu'à ce qu'il passe. Sa deuxième étape vérifie que le retriever de LangChain renvoie
   exactement les passages de ta propre recherche.

## À retenir

- LangChain fournit des interfaces communes et une façon d'enchaîner les étapes.
- Chaque pièce correspond à une fonction que tu as écrite dans les modules précédents.
- Le framework apporte l'interchangeabilité, le streaming et l'écosystème. Il coûte des valeurs par défaut
  cachées, des couches et une dépendance qui bouge.
- Connaître ce qu'il y a dessous permet de choisir, et de déboguer.

## Dans l'assistant

La version LangChain vit dans `assistant/rag_langchain.py`, à côté de la version écrite à la main. Les deux
lisent le même index et donnent les mêmes passages. Le reste du cours continue sur la version à la main.
