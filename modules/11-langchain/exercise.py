"""Module 11: LangChain. Read LESSON.md first. Needs the dependency group: uv sync --group langchain

Run this file to ask the LangChain version of the assistant a question, streamed.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from assistant.config import settings
from assistant.rag import RAG_PROMPT
from assistant.store import reference_index, reference_path


def format_docs(docs: list[Document]) -> str:
    """Turns retrieved documents into the numbered list of passages of module 07.

    A LangChain Document has .page_content (the text) and .metadata (a dict with "source" and "heading").
    Expected format for each document, separated by blank lines:
        [1] cache.md (Cache > Storing Items)
        Use the put method.
    """
    raise NotImplementedError


def build_retriever(k: int = 5) -> VectorStoreRetriever:
    """A LangChain retriever over the index you already built.

    1. embeddings = OpenAIEmbeddings(model=settings.embed_model, base_url=settings.embed_base_url,
                                     api_key=settings.embed_api_key, check_embedding_ctx_length=False)
    2. store = Chroma(persist_directory=str(reference_path()), collection_name="docs",
                      embedding_function=embeddings)
    3. return store.as_retriever(search_kwargs={"k": k})
    """
    reference_index()  # builds the index if this is the first use
    raise NotImplementedError


def build_chain(k: int = 5) -> Runnable:
    """The whole RAG as one chain: question (str) in, answer (str) out.

    Components:
      prompt = ChatPromptTemplate.from_messages([("system", RAG_PROMPT),
                                                 ("human", "Passages:\\n\\n{passages}\\n\\nQuestion: {question}")])
      model  = ChatOpenAI(model=settings.chat_model, base_url=settings.chat_base_url,
                          api_key=settings.chat_api_key, temperature=0)
    Assembly, with the | operator:
      a dict {"passages": retriever | format_docs, "question": RunnablePassthrough()} feeds the prompt,
      the prompt feeds the model, the model feeds StrOutputParser().
    """
    raise NotImplementedError


if __name__ == "__main__":
    chain = build_chain()
    print("Pose une question sur Laravel (ligne vide pour quitter).")
    while question := input("> ").strip():
        for piece in chain.stream(question):
            print(piece, end="", flush=True)
        print("\n")
