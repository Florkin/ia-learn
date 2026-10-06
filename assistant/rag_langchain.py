"""The RAG of module 07 rebuilt with LangChain: reference brick for module 11."""

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
    return "\n\n".join(
        f"[{number}] {doc.metadata['source']} ({doc.metadata['heading']})\n{doc.page_content}"
        for number, doc in enumerate(docs, start=1)
    )


def build_retriever(k: int = 5) -> VectorStoreRetriever:
    reference_index()  # builds the index if this is the first use
    embeddings = OpenAIEmbeddings(
        model=settings.embed_model,
        base_url=settings.embed_base_url,
        api_key=settings.embed_api_key,
        # By default LangChain sends token ids computed with OpenAI's tokenizer, which other servers reject.
        check_embedding_ctx_length=False,
    )
    store = Chroma(persist_directory=str(reference_path()), collection_name="docs", embedding_function=embeddings)
    return store.as_retriever(search_kwargs={"k": k})


def build_chain(k: int = 5) -> Runnable:
    prompt = ChatPromptTemplate.from_messages(
        [("system", RAG_PROMPT), ("human", "Passages:\n\n{passages}\n\nQuestion: {question}")]
    )
    model = ChatOpenAI(
        model=settings.chat_model, base_url=settings.chat_base_url, api_key=settings.chat_api_key, temperature=0
    )
    inputs = {"passages": build_retriever(k) | format_docs, "question": RunnablePassthrough()}
    return inputs | prompt | model | StrOutputParser()
