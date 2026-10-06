"""Talking to a chat model: reference bricks for modules 01, 02, 03 and 10."""

from collections.abc import Iterator
from functools import lru_cache
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

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


# --- Module 02: generation settings ------------------------------------------------------


def stream_answer(question: str, system: str = SYSTEM_PROMPT, temperature: float = 0.0) -> Iterator[str]:
    events = client().chat.completions.create(
        model=settings.chat_model,
        messages=build_messages(system, [], question),
        temperature=temperature,
        stream=True,
    )
    for event in events:
        if event.choices and event.choices[0].delta.content:
            yield event.choices[0].delta.content


def variants(prompt: str, temperature: float, n: int = 3) -> list[str]:
    answers = []
    for _ in range(n):
        response = client().chat.completions.create(
            model=settings.chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        answers.append(response.choices[0].message.content.strip())
    return answers


# --- Module 03: structured output --------------------------------------------------------

ANALYSIS_PROMPT = """You analyze questions sent to a Laravel documentation assistant. Reply with a JSON object:
- "language": "fr" or "en", the language the question is written in.
- "about_laravel": true if the question is about Laravel or web development with it, false otherwise. \
A question that mentions a code identifier or a technical term is about Laravel.
- "search_query": the question rewritten as a short English search query. Keep code identifiers unchanged."""


class QuestionAnalysis(BaseModel):
    language: Literal["fr", "en"]
    about_laravel: bool
    search_query: str


def analyze_question(question: str) -> QuestionAnalysis:
    response = client().chat.completions.create(
        model=settings.chat_model,
        messages=build_messages(ANALYSIS_PROMPT, [], question),
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "question_analysis", "schema": QuestionAnalysis.model_json_schema()},
        },
    )
    return QuestionAnalysis.model_validate_json(response.choices[0].message.content)
