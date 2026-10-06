"""Module 13: training. Read LESSON.md first. Needs the dependency groups: uv sync --all-groups

Run this file to train a classifier, then to make one overfit on purpose.
"""

import torch
from torch import nn

from assistant.classifier import Dataset, accuracy, load_dataset, make_model, predict


def train(model: nn.Module, data: Dataset, epochs: int = 30, lr: float = 1e-2, batch_size: int = 64) -> list[dict]:
    """Trains the model in place and returns one measure per epoch.

    Before the loop:
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)
      loss_function = nn.CrossEntropyLoss()

    For each epoch, numbered from 1:
      1. Shuffle the training examples: order = torch.randperm(len(data.X_train)).
      2. For each batch of `batch_size` indices taken from `order`:
           predictions = model(data.X_train[batch])
           loss = loss_function(predictions, data.y_train[batch])
           optimizer.zero_grad()   # forget the gradients of the previous batch
           loss.backward()         # compute how each parameter should move
           optimizer.step()        # move the parameters
      3. Measure, inside `with torch.no_grad():`, and append to the history:
           {"epoch": ..., "train_loss": ..., "val_loss": ..., "val_accuracy": ...}
         train_loss is the loss on the whole training set, val_loss on data.X_val / data.y_val.
         accuracy(model, X, y) is provided. Use .item() to turn a one-value tensor into a float.
    """
    raise NotImplementedError


def show(history: list[dict], epochs: tuple[int, ...]) -> None:
    print("époque  perte entraînement  perte validation  précision validation")
    for entry in history:
        if entry["epoch"] in epochs:
            print(f"{entry['epoch']:6d}  {entry['train_loss']:18.3f}  {entry['val_loss']:16.3f}  {entry['val_accuracy']:20.3f}")


if __name__ == "__main__":
    torch.manual_seed(0)
    data = load_dataset()
    n_features, n_classes = data.X_train.shape[1], len(data.labels)
    print(f"{len(data.X_train)} exemples d'entraînement, {len(data.X_val)} de validation, {n_classes} sections\n")

    print("1. Un modèle linéaire sur toutes les données")
    model = make_model(n_features, n_classes)
    show(train(model, data, epochs=30), epochs=(1, 2, 5, 10, 20, 30))
    for question in ("Comment hacher un mot de passe ?", "Comment définir une relation entre deux modèles ?"):
        print(f"   {question}  →  {predict(model, data.labels, question)}")

    print("\n2. Un modèle plus gros sur 150 exemples seulement")
    small = Dataset(data.X_train[:150], data.y_train[:150], data.X_val, data.y_val, data.labels)
    big_model = make_model(n_features, n_classes, hidden=512)
    show(train(big_model, small, epochs=300, lr=1e-3), epochs=(1, 10, 20, 50, 100, 200, 300))
