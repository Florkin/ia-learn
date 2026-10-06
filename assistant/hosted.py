"""Running the same prompt on several models, local and hosted: reference brick for module 10."""

import json
import time
import urllib.request
from dataclasses import dataclass
from functools import lru_cache

from openai import OpenAI

from assistant.config import OPENROUTER_URL, settings
from assistant.rag import build_prompt
from assistant.retrieval import vector_search


@dataclass(frozen=True)
class Target:
    name: str
    base_url: str
    api_key: str
    model: str
    price_in: float = 0.0  # US dollars per million input tokens
    price_out: float = 0.0  # US dollars per million output tokens


@dataclass
class Run:
    target: str
    answer: str
    seconds: float
    prompt_tokens: int
    completion_tokens: int
    cost: float  # US dollars


def local_target() -> Target:
    return Target(f"local {settings.chat_model}", settings.chat_base_url, settings.chat_api_key, settings.chat_model)


@lru_cache
def openrouter_prices() -> dict[str, tuple[float, float]]:
    """Public price list of OpenRouter: model id -> (input, output) in dollars per million tokens."""
    with urllib.request.urlopen(f"{OPENROUTER_URL}/models", timeout=30) as response:
        models = json.load(response)["data"]
    return {
        model["id"]: (float(model["pricing"]["prompt"]) * 1e6, float(model["pricing"]["completion"]) * 1e6)
        for model in models
    }


def hosted_targets() -> list[Target]:
    """The models listed in HOSTED_MODELS, served by OpenRouter with the key from .env."""
    prices = openrouter_prices()
    unknown = [model for model in settings.hosted_models if model not in prices]
    if unknown:
        raise ValueError(f"modèles inconnus d'OpenRouter : {unknown}. Corrige HOSTED_MODELS dans .env.")
    return [
        Target(model, OPENROUTER_URL, settings.openrouter_api_key, model, *prices[model])
        for model in settings.hosted_models
    ]


# --- Module 10: hosted models --------------------------------------------------------------


def cost(prompt_tokens: int, completion_tokens: int, price_in: float, price_out: float) -> float:
    return (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000


def ask_target(target: Target, messages: list[dict]) -> Run:
    client = OpenAI(base_url=target.base_url, api_key=target.api_key)
    start = time.perf_counter()
    response = client.chat.completions.create(model=target.model, messages=messages, temperature=0)
    seconds = time.perf_counter() - start
    usage = response.usage
    return Run(
        target=target.name,
        answer=response.choices[0].message.content,
        seconds=seconds,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        cost=cost(usage.prompt_tokens, usage.completion_tokens, target.price_in, target.price_out),
    )


def compare(question: str, targets: list[Target], k: int = 5) -> list[Run]:
    """Retrieves the passages once, then asks every target the same prompt."""
    messages = build_prompt(question, vector_search(question, k))
    return [ask_target(target, messages) for target in targets]
