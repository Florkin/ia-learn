from course.harness import Check, require

require("torch", "uv sync --all-groups")

import torch

from assistant import classifier

check = Check(__file__, reference="assistant.classifier")
ex = check.exercise

torch.manual_seed(0)
data = classifier.load_dataset()
model = classifier.make_model(data.X_train.shape[1], len(data.labels))
untrained = classifier.accuracy(model, data.X_val, data.y_val)
majority = torch.bincount(data.y_val).max().item() / len(data.y_val)

with check.step("train renvoie une mesure par époque"):
    history = ex.train(model, data, epochs=20, lr=1e-2)
    assert isinstance(history, list) and len(history) == 20, f"20 entrées attendues (une par époque), obtenu : {history!r:.200}"
    expected_keys = {"epoch", "train_loss", "val_loss", "val_accuracy"}
    assert all(expected_keys <= set(entry) for entry in history), f"chaque entrée doit contenir {sorted(expected_keys)}, obtenu : {history[0]}"
    assert [entry["epoch"] for entry in history] == list(range(1, 21)), "les époques se numérotent de 1 à 20"
    assert all(isinstance(entry["train_loss"], float) for entry in history), "les mesures doivent être des nombres Python : utilise .item() sur les tenseurs"

with check.step("la perte d'entraînement baisse d'époque en époque"):
    first, last = history[0]["train_loss"], history[-1]["train_loss"]
    assert last < first * 0.6, (
        f"la perte devait nettement baisser, obtenu : {first:.3f} à la première époque, {last:.3f} à la dernière. "
        "Vérifie l'ordre : optimizer.zero_grad(), loss.backward(), optimizer.step()."
    )

with check.step("le modèle a appris : il classe bien des passages qu'il n'a jamais vus"):
    trained = classifier.accuracy(model, data.X_val, data.y_val)
    print(f"       précision de validation : {untrained:.3f} avant entraînement, {trained:.3f} après (classe majoritaire : {majority:.3f})")
    assert trained >= 0.85, f"une précision d'au moins 0.85 était attendue sur la validation, obtenu : {trained:.3f}"
    assert abs(history[-1]["val_accuracy"] - trained) < 1e-6, (
        "val_accuracy de la dernière époque doit être la précision mesurée sur data.X_val et data.y_val"
    )

with check.step("la perte de validation est mesurée sur les données de validation"):
    with torch.no_grad():
        expected = torch.nn.functional.cross_entropy(model(data.X_val), data.y_val).item()
    assert abs(history[-1]["val_loss"] - expected) < 1e-4, f"val_loss attendue : {expected:.4f}, obtenu : {history[-1]['val_loss']:.4f}"

check.finish()
