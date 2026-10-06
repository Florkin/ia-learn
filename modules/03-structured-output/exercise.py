"""Module 03: structured output. Read LESSON.md first.

Run this file to analyze a few questions and print the resulting objects.
"""

from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

from assistant.config import settings

ANALYSIS_PROMPT = """You analyze questions sent to a Laravel documentation assistant. Reply with a JSON object:
- "language": "fr" or "en", the language the question is written in.
- "about_laravel": true if the question is about Laravel or web development with it, false otherwise. \
A question that mentions a code identifier or a technical term is about Laravel.
- "search_query": the question rewritten as a short English search query. Keep code identifiers unchanged."""

client = OpenAI(base_url=settings.chat_base_url, api_key=settings.chat_api_key)


class QuestionAnalysis(BaseModel):
    language: Literal["fr", "en"]
    about_laravel: bool
    # Add the third field described in ANALYSIS_PROMPT.


def analyze_question(question: str) -> QuestionAnalysis:
    """Asks the model to analyze the question and returns a validated QuestionAnalysis.

    Send ANALYSIS_PROMPT as the system message, temperature 0, and constrain the output with
        response_format={"type": "json_schema",
                         "json_schema": {"name": "question_analysis", "schema": <the JSON schema>}}
    QuestionAnalysis.model_json_schema() builds the schema,
    QuestionAnalysis.model_validate_json(text) turns the model's answer into an object.
    """
    raise NotImplementedError


if __name__ == "__main__":
    questions = [
        "Comment mettre en cache le résultat d'une requête pendant dix minutes ?",
        "How do I hash a password?",
        "Quel temps fait-il à Lyon ?",
        "À quoi sert whereBelongsTo ?",
    ]
    for question in questions:
        print(f"{question}\n  {analyze_question(question)!r}")
