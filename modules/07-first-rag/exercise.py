"""Module 07: first RAG. Read LESSON.md first.

Run this file to ask the assistant questions about the Laravel documentation.
"""

from assistant.chunking import Chunk
from assistant.llm import chat
from assistant.rag import Answer
from assistant.store import query_index, reference_index

RAG_PROMPT = """You answer questions about Laravel using only the numbered passages provided by the user.
- Answer in the language of the question.
- Cite the passages you used with their number in square brackets, for example [2].
- Be brief: a few sentences, and at most one code example copied from the passages.
- If the passages do not contain the answer, say that the documentation provided does not cover it. \
Do not use outside knowledge."""


def build_prompt(question: str, passages: list[Chunk]) -> list[dict]:
    """Returns two messages: RAG_PROMPT as the system message, then one user message.

    The user message lists the passages, numbered from 1, each with its source and heading:
        [1] cache.md (Cache > Storing Items)
        Use the put method to store an item.
    and ends with the question.
    """
    raise NotImplementedError


def answer(question: str, k: int = 5) -> Answer:
    """Retrieves the k closest passages, asks the model, returns Answer(text, sources).

    query_index(question, reference_index(), k) searches the index of the whole documentation.
    chat(messages) sends messages to the model and returns the text of its answer.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print("Pose une question sur Laravel (ligne vide pour quitter).")
    while question := input("> ").strip():
        result = answer(question)
        print(f"\n{result.text}\n")
        for number, passage in enumerate(result.sources, start=1):
            print(f"  [{number}] {passage.source}  {passage.heading}")
        print()
