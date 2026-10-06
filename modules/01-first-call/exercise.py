"""Module 01: first call to a language model. Read LESSON.md first.

Run this file to chat with the model in your terminal.
"""

from openai import OpenAI

from assistant.config import settings

SYSTEM_PROMPT = "You are a concise assistant. Answer in the language of the question."

client = OpenAI(base_url=settings.chat_base_url, api_key=settings.chat_api_key)


def build_messages(system: str, history: list[dict], question: str) -> list[dict]:
    """Returns the messages to send: the system prompt, then the past turns, then the new question.

    Every message is a dict {"role": ..., "content": ...}. `history` already has that shape.
    """
    raise NotImplementedError


def ask(question: str, history: list[dict] | None = None, system: str = SYSTEM_PROMPT) -> str:
    """Sends the conversation to the model and returns the text of its answer.

    Call client.chat.completions.create(model=settings.chat_model, messages=..., temperature=0)
    and read the text from the first choice of the response.
    """
    raise NotImplementedError


if __name__ == "__main__":
    # A tiny terminal chat. The model only knows what is resent in `history` on every call.
    history: list[dict] = []
    print("Pose une question (ligne vide pour quitter).")
    while question := input("> ").strip():
        reply = ask(question, history)
        print(reply)
        history += [{"role": "user", "content": question}, {"role": "assistant", "content": reply}]
