import re

from course.harness import Check, require

require("langchain_core", "uv sync --group langchain")

from langchain_core.documents import Document

from assistant import retrieval

check = Check(__file__, reference="assistant.rag_langchain")
ex = check.exercise

QUESTION = "Comment éviter qu'une tâche planifiée se lance deux fois en même temps ?"

with check.step("format_docs numérote les documents comme build_prompt au module 7"):
    docs = [
        Document(page_content="Use the put method.", metadata={"source": "cache.md", "heading": "Cache > Storing Items"}),
        Document(page_content="Named routes.", metadata={"source": "routing.md", "heading": "Routing > Named Routes"}),
    ]
    text = ex.format_docs(docs)
    assert isinstance(text, str), f"une chaîne est attendue, obtenu : {type(text).__name__}"
    for number, doc in enumerate(docs, start=1):
        assert f"[{number}]" in text and doc.page_content in text and doc.metadata["source"] in text, (
            f"le document {number} doit apparaître avec son numéro, sa source et son texte. Obtenu :\n{text}"
        )

with check.step("le retriever LangChain renvoie les mêmes passages que ta recherche du module 6"):
    docs = ex.build_retriever(k=5).invoke(QUESTION)
    expected = retrieval.vector_search(QUESTION, 5)
    assert [doc.page_content for doc in docs] == [chunk.text for chunk in expected], (
        "les passages diffèrent de ceux de vector_search. Vérifie le dossier de l'index, le nom de la "
        f"collection et k. Sources obtenues : {[doc.metadata.get('source') for doc in docs]}"
    )

with check.step("la chaîne répond à partir des passages et cite ses sources"):
    chain = ex.build_chain()
    answer = chain.invoke("Avec le Laravel AI SDK, quelle commande Artisan crée un agent ?")
    assert isinstance(answer, str), f"la chaîne doit se terminer par un StrOutputParser, obtenu : {type(answer).__name__}"
    assert "make:agent" in answer, f"la réponse devait contenir `make:agent`, obtenu : {answer!r}"
    assert re.search(r"\[\d\]", answer), f"la réponse devait citer un passage, obtenu : {answer!r}"

with check.step("la même chaîne sait répondre au fil de l'eau, sans code supplémentaire"):
    pieces = list(chain.stream("Comment hacher un mot de passe ?"))
    assert len(pieces) >= 2 and all(isinstance(piece, str) for piece in pieces), "chain.stream devait produire plusieurs morceaux de texte"

check.finish()
