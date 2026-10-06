from course.harness import Check

check = Check(__file__, reference="assistant.llm")
ex = check.exercise

with check.step("build_messages place le prompt système en premier et la question en dernier"):
    history = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}]
    messages = ex.build_messages("SYS", history, "Q?")
    assert isinstance(messages, list), f"une liste de messages est attendue, obtenu : {type(messages).__name__}"
    assert messages[0] == {"role": "system", "content": "SYS"}, f"premier message obtenu : {messages[0]}"
    assert messages[1:3] == history, "l'historique doit être repris tel quel, entre le prompt système et la question"
    assert messages[-1] == {"role": "user", "content": "Q?"}, f"dernier message obtenu : {messages[-1]}"
    assert len(history) == 2, "build_messages ne doit pas modifier la liste `history` qu'elle reçoit"

with check.step("ask renvoie le texte de la réponse du modèle"):
    reply = ex.ask("Reply with the single word: pong")
    assert isinstance(reply, str), f"une chaîne est attendue, obtenu : {type(reply).__name__}"
    assert "pong" in reply.lower(), f"la réponse devait contenir « pong », obtenu : {reply!r}"

with check.step("ask transmet l'historique, le modèle retrouve une information donnée plus tôt"):
    history = [
        {"role": "user", "content": "My name is Ada."},
        {"role": "assistant", "content": "Nice to meet you, Ada."},
    ]
    reply = ex.ask("What is my name? Answer with the name only.", history)
    assert "ada" in reply.lower(), f"le modèle devait retrouver le prénom Ada, obtenu : {reply!r}"

check.finish()
