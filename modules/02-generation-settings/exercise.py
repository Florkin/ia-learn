"""Module 02: generation settings. Read LESSON.md first.

Run this file to watch an answer arrive token by token, then compare temperatures.
"""

from collections.abc import Iterator

from openai import OpenAI

from assistant.config import settings

SYSTEM_PROMPT = "You are a concise assistant. Answer in the language of the question."

client = OpenAI(base_url=settings.chat_base_url, api_key=settings.chat_api_key)


def stream_answer(question: str, system: str = SYSTEM_PROMPT, temperature: float = 0.0) -> Iterator[str]:
    """Yields the answer piece by piece, as the model produces it.

    Pass stream=True to client.chat.completions.create(...) and loop over the events.
    The text of an event is in event.choices[0].delta.content. It can be None or empty: skip those.
    """
    raise NotImplementedError


def variants(prompt: str, temperature: float, n: int = 3) -> list[str]:
    """Sends the same prompt n times at the given temperature and returns the n answers, stripped."""
    raise NotImplementedError


if __name__ == "__main__":
    question = (
        "Avec le Laravel AI SDK de Laravel 13, quelle commande Artisan crée un agent "
        "et quelle méthode lui envoie un prompt ? Donne un exemple de code court."
    )
    print(f"> {question}\n")
    for piece in stream_answer(question):
        print(piece, end="", flush=True)
    print("\n")

    for temperature in (0, 0.8, 1.5):
        names = variants("Invent a name for a coffee shop. Reply with the name only.", temperature, n=5)
        print(f"température {temperature} : {names}")
