"""Retrieval-augmented generation, written by hand: reference brick for module 07."""

from dataclasses import dataclass

from assistant.chunking import Chunk
from assistant.llm import chat
from assistant.store import query_index, reference_index

RAG_PROMPT = """You answer questions about Laravel using only the numbered passages provided by the user.
- Answer in the language of the question.
- Cite the passages you used with their number in square brackets, for example [2].
- Be brief: a few sentences, and at most one code example copied from the passages.
- If the passages do not contain the answer, say that the documentation provided does not cover it. \
Do not use outside knowledge."""


@dataclass
class Answer:
    text: str
    sources: list[Chunk]  # the passages given to the model, in the order they were numbered


def build_prompt(question: str, passages: list[Chunk]) -> list[dict]:
    numbered = "\n\n".join(
        f"[{number}] {passage.source} ({passage.heading})\n{passage.text}"
        for number, passage in enumerate(passages, start=1)
    )
    return [
        {"role": "system", "content": RAG_PROMPT},
        {"role": "user", "content": f"Passages:\n\n{numbered}\n\nQuestion: {question}"},
    ]


def answer(question: str, k: int = 5) -> Answer:
    passages = query_index(question, reference_index(), k)
    return Answer(chat(build_prompt(question, passages)), passages)
