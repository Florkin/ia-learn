from assistant import agent
from course.harness import Check

check = Check(__file__, reference="assistant.agent")
ex = check.exercise


def tool_request(name: str, arguments: str, id: str = "call_1") -> dict:
    return {"role": "assistant", "content": "", "tool_calls": [{"id": id, "type": "function", "function": {"name": name, "arguments": arguments}}]}


class ScriptedModel:
    """Stands in for the model: replays prepared messages and records what the agent sent."""

    def __init__(self, *replies: dict, repeat_last: bool = False):
        self.replies, self.repeat_last, self.seen = list(replies), repeat_last, []

    def __call__(self, messages: list[dict]) -> dict:
        self.seen.append([dict(message) for message in messages])
        index = min(len(self.seen) - 1, len(self.replies) - 1) if self.repeat_last else len(self.seen) - 1
        return self.replies[index]


with check.step("sans demande d'outil, la réponse du modèle est renvoyée telle quelle"):
    model = ScriptedModel({"role": "assistant", "content": "Bonjour !"})
    result = ex.run_agent("Salut", complete=model)
    assert isinstance(result, agent.AgentResult), f"un AgentResult est attendu, obtenu : {type(result).__name__}"
    assert (result.answer, result.tool_calls, result.steps) == ("Bonjour !", [], 1), f"obtenu : {result}"
    first = model.seen[0]
    assert first[0]["role"] == "system" and first[-1] == {"role": "user", "content": "Salut"}, (
        "le premier appel doit contenir le prompt système AGENT_PROMPT puis la question"
    )

with check.step("quand le modèle demande un outil, l'agent l'exécute et renvoie le résultat au modèle"):
    model = ScriptedModel(tool_request("search_docs", '{"query": "hash a password"}'), {"role": "assistant", "content": "Use Hash::make [1]."})
    result = ex.run_agent("Comment hacher un mot de passe ?", complete=model)
    assert result.steps == 2 and result.answer == "Use Hash::make [1].", f"deux appels au modèle étaient attendus, obtenu : {result}"
    assert len(result.tool_calls) == 1 and result.tool_calls[0]["name"] == "search_docs", f"tool_calls obtenu : {result.tool_calls}"
    second = model.seen[1]
    assert second[-2].get("tool_calls"), "le message du modèle qui demande l'outil doit être ajouté à la conversation"
    tool_message = second[-1]
    assert tool_message["role"] == "tool" and tool_message.get("tool_call_id") == "call_1", (
        f"le résultat doit revenir dans un message de rôle tool portant l'identifiant de la demande, obtenu : {tool_message}"
    )
    assert "hashing.md" in tool_message["content"], "le contenu du message tool doit être le résultat de la recherche"

with check.step("la boucle s'arrête à max_steps même si le modèle réclame toujours un outil"):
    model = ScriptedModel(tool_request("search_docs", '{"query": "routes"}'), repeat_last=True)
    result = ex.run_agent("Boucle", max_steps=3, complete=model)
    assert len(model.seen) == 3, f"3 appels au modèle attendus, pas plus, obtenu : {len(model.seen)}"
    assert result.steps == 3 and len(result.tool_calls) == 3, f"obtenu : steps={result.steps}, {len(result.tool_calls)} appels d'outil"
    assert isinstance(result.answer, str) and result.answer, "sans réponse du modèle, l'agent doit rendre un message d'échec, pas None"

with check.step("un outil inconnu ou des arguments invalides ne font pas planter l'agent"):
    model = ScriptedModel(
        tool_request("delete_everything", "{}", id="call_a"),
        tool_request("search_docs", "{not json", id="call_b"),
        {"role": "assistant", "content": "Désolé."},
    )
    result = ex.run_agent("Supprime tout", complete=model)
    assert result.answer == "Désolé." and result.steps == 3, f"obtenu : {result}"
    for step, id in ((1, "call_a"), (2, "call_b")):
        reply = model.seen[step][-1]
        assert reply["role"] == "tool" and reply.get("tool_call_id") == id and "rror" in reply["content"], (
            f"une demande invalide doit recevoir un message tool qui décrit l'erreur, obtenu : {reply}"
        )

with check.step("avec le vrai modèle, une question sur Laravel déclenche une recherche"):
    result = ex.run_agent("Comment hacher un mot de passe et vérifier ensuite qu'il correspond ?")
    assert any(call["name"] == "search_docs" for call in result.tool_calls), f"aucune recherche lancée, réponse : {result.answer!r}"
    assert "Hash" in result.answer, f"la réponse devait s'appuyer sur la façade Hash, obtenu : {result.answer!r}"

with check.step("avec le vrai modèle, une salutation ne déclenche aucune recherche"):
    result = ex.run_agent("Salut, ça va ?")
    assert result.tool_calls == [] and result.answer.strip(), f"obtenu : {result}"

check.finish()
