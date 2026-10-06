"""Module 06: vector store. Read LESSON.md first.

Run this file to index the sample pages on disk, then search them with and without a filter.
"""

from chromadb.api.models.Collection import Collection

from assistant.chunking import Chunk, chunk_corpus
from assistant.config import DATA_DIR, settings
from assistant.embeddings import embed
from assistant.store import open_collection


def build_index(chunks: list[Chunk], collection: Collection) -> int:
    """Stores every chunk in the collection and returns the number of items the collection holds.

    One call to collection.upsert(ids=..., embeddings=..., documents=..., metadatas=...) with four
    lists of the same length:
      ids         the chunk ids
      embeddings  embed() of each chunk.content
      documents   each chunk.text
      metadatas   one dict per chunk: {"source": ..., "section": ..., "heading": ...}
    collection.count() gives the size of the collection.
    """
    raise NotImplementedError


def query_index(question: str, collection: Collection, k: int = 5, where: dict | None = None) -> list[Chunk]:
    """Returns the k chunks closest to the question, best first. `where` filters on metadata.

    result = collection.query(query_embeddings=embed([question]), n_results=k, where=where)
    The query accepts several questions at once, so every field of the result is a list of lists:
    result["ids"][0], result["documents"][0] and result["metadatas"][0] belong to our single question.
    Rebuild one Chunk per hit from these three lists.
    """
    raise NotImplementedError


if __name__ == "__main__":
    collection = open_collection(DATA_DIR / f"learner-{settings.learner or 'demo'}-06")
    print(f"Avant indexation : {collection.count()} passages")
    print(f"Après indexation : {build_index(chunk_corpus(sample=True), collection)} passages")

    question = "How do I store something?"
    for where in (None, {"section": "Database"}, {"source": "cache.md"}):
        print(f"\n> {question}   filtre : {where}")
        for chunk in query_index(question, collection, k=3, where=where):
            print(f"  {chunk.source:24s} {chunk.heading}")
