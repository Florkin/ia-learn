"""Module 10: hosted models. Read LESSON.md first.

Run this file to ask the same question to the local model and to the hosted models of HOSTED_MODELS.
"""

import time

from openai import OpenAI

from assistant.config import settings
from assistant.hosted import Run, Target, hosted_targets, local_target
from assistant.rag import build_prompt
from assistant.retrieval import vector_search


def cost(prompt_tokens: int, completion_tokens: int, price_in: float, price_out: float) -> float:
    """Price of one call in US dollars. Prices are given in dollars per million tokens."""
    raise NotImplementedError


def ask_target(target: Target, messages: list[dict]) -> Run:
    """Sends the messages to one target and reports what it cost.

    Build a client for the target: OpenAI(base_url=target.base_url, api_key=target.api_key).
    Call target.model at temperature 0 and time the call with time.perf_counter().
    response.usage holds prompt_tokens and completion_tokens.
    Return Run(target=target.name, answer=..., seconds=..., prompt_tokens=..., completion_tokens=..., cost=...).
    """
    raise NotImplementedError


def compare(question: str, targets: list[Target], k: int = 5) -> list[Run]:
    """Asks every target the same RAG prompt and returns one Run per target, in order.

    Retrieve the passages once with vector_search(question, k) and build the messages once with
    build_prompt(question, passages): the models must be compared on identical input.
    """
    raise NotImplementedError


if __name__ == "__main__":
    targets = [local_target()]
    if settings.openrouter_api_key:
        targets += hosted_targets()
    else:
        print("OPENROUTER_API_KEY est vide dans .env : seul le modèle local est interrogé.\n")

    questions = [
        "Comment éviter qu'une tâche planifiée se lance deux fois en même temps ?",
        "Quelle est la différence entre une policy et une gate ?",
    ]
    for question in questions:
        print(f"> {question}\n")
        runs = compare(question, targets)
        for run in runs:
            print(f"--- {run.target} ---\n{run.answer}\n")
        print(f"{'modèle':36s} {'durée':>7s} {'entrée':>7s} {'sortie':>7s} {'coût ($)':>10s} {'pour 1000 questions':>20s}")
        for run in runs:
            print(
                f"{run.target:36s} {run.seconds:6.1f}s {run.prompt_tokens:7d} {run.completion_tokens:7d} "
                f"{run.cost:10.6f} {run.cost * 1000:19.2f}$"
            )
        print()
