"""Module 12: tools and agents. Read LESSON.md first.

Run this file to talk to an assistant that decides by itself when to search the documentation.
"""

from collections.abc import Callable

from assistant.agent import AGENT_PROMPT, AgentResult, call_tool, complete


def run_agent(question: str, max_steps: int = 4, complete: Callable[[list[dict]], dict] = complete) -> AgentResult:
    """Lets the model answer, running the tools it asks for, for at most max_steps model calls.

    Start the conversation with AGENT_PROMPT (system) and the question (user). Then loop:
      1. message = complete(messages) asks the model. Append this message to the conversation.
      2. If message has no "tool_calls", it is the final answer: return
         AgentResult(message["content"], tool_calls, number of model calls so far).
      3. Otherwise, for each call in message["tool_calls"]:
           name = call["function"]["name"], raw_arguments = call["function"]["arguments"] (a JSON string)
           result = call_tool(name, raw_arguments)   runs the tool, returns text (an error text if invalid)
           record {"name": name, "arguments": raw_arguments} in your list of tool calls
           append {"role": "tool", "tool_call_id": call["id"], "content": result} to the conversation
    After max_steps model calls without a final answer, return an AgentResult whose answer says so.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print("Pose une question, ou dis bonjour (ligne vide pour quitter).")
    while question := input("> ").strip():
        result = run_agent(question)
        for call in result.tool_calls:
            print(f"  [outil] {call['name']} {call['arguments']}")
        print(f"\n{result.answer}\n  ({result.steps} appel(s) au modèle)\n")
