"""A tool-calling loop written by hand: reference brick for module 12."""

import json
from collections.abc import Callable
from dataclasses import dataclass

from assistant.config import settings
from assistant.llm import client
from assistant.retrieval import vector_search

AGENT_PROMPT = """You are an assistant for the Laravel framework. \
Your own knowledge of Laravel is outdated and must not be used.
- Whenever the user asks anything about Laravel, PHP or one of its tools, you MUST call the search_docs tool \
before answering, then answer using only the passages it returns.
- You may call the tool again with another query if the passages are not enough.
- Cite the passages you used with their number in square brackets, for example [2]. Be brief.
- Answer in the language of the question. Only greetings and small talk are answered without the tool."""

# What the model is told about the tool: a name, a description and the JSON schema of its arguments.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the Laravel documentation. Returns the most relevant passages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look for, as a short question or keywords."}
                },
                "required": ["query"],
            },
        },
    }
]


def search_docs(query: str) -> str:
    """The tool itself: ordinary code, run by us when the model asks for it."""
    passages = vector_search(query, 4)
    return "\n\n".join(f"[{n}] {p.source} ({p.heading})\n{p.text}" for n, p in enumerate(passages, start=1))


# The only functions the model is allowed to trigger.
TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {"search_docs": search_docs}


def complete(messages: list[dict]) -> dict:
    """One model call with the tools declared. Returns the assistant message as a plain dict."""
    response = client().chat.completions.create(
        model=settings.chat_model, messages=messages, tools=TOOLS, temperature=0
    )
    return response.choices[0].message.model_dump(exclude_none=True)


@dataclass
class AgentResult:
    answer: str
    tool_calls: list[dict]  # [{"name": ..., "arguments": {...}}, ...] in the order they were requested
    steps: int  # number of model calls


def call_tool(name: str, raw_arguments: str) -> str:
    """Runs a tool requested by the model. Its name and arguments are untrusted input: errors go back as text."""
    if name not in TOOL_FUNCTIONS:
        return f"Error: unknown tool {name!r}. Available tools: {', '.join(TOOL_FUNCTIONS)}."
    try:
        return TOOL_FUNCTIONS[name](**json.loads(raw_arguments))
    except (json.JSONDecodeError, TypeError) as error:
        return f"Error: invalid arguments for {name}: {error}"


# --- Module 12: the agent loop ---------------------------------------------------------------


def run_agent(question: str, max_steps: int = 4, complete: Callable[[list[dict]], dict] = complete) -> AgentResult:
    messages = [{"role": "system", "content": AGENT_PROMPT}, {"role": "user", "content": question}]
    tool_calls: list[dict] = []
    for step in range(1, max_steps + 1):
        message = complete(messages)
        messages.append(message)
        if not message.get("tool_calls"):
            return AgentResult(message.get("content") or "", tool_calls, step)
        for call in message["tool_calls"]:
            name, raw_arguments = call["function"]["name"], call["function"]["arguments"]
            tool_calls.append({"name": name, "arguments": raw_arguments})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": call_tool(name, raw_arguments)})
    return AgentResult("Je n'ai pas pu conclure dans le nombre d'étapes autorisé.", tool_calls, max_steps)
