"""Talking to a chat model: reference bricks for modules 01, 02, 03 and 10."""

from functools import lru_cache

from openai import OpenAI

from assistant.config import settings

SYSTEM_PROMPT = "You are a concise assistant. Answer in the language of the question."


@lru_cache
def client(base_url: str | None = None, api_key: str | None = None) -> OpenAI:
    """OpenAI-compatible client. Defaults to the chat endpoint configured in .env."""
    return OpenAI(base_url=base_url or settings.chat_base_url, api_key=api_key or settings.chat_api_key)


# --- Module 01: first call ---------------------------------------------------------------


def build_messages(system: str, history: list[dict], question: str) -> list[dict]:
    return [{"role": "system", "content": system}, *history, {"role": "user", "content": question}]


def ask(question: str, history: list[dict] | None = None, system: str = SYSTEM_PROMPT) -> str:
    response = client().chat.completions.create(
        model=settings.chat_model,
        messages=build_messages(system, history or [], question),
        temperature=0,
    )
    return response.choices[0].message.content
