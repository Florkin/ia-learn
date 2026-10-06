"""Shared plumbing for the modules' check.py scripts.

A check loads one exercise file, runs named steps against it and stops at the first failure
with a message the learner can act on. COURSE_MODE selects which file is checked:

    learner    (default) learners/<LEARNER>/<module>.py, created from the skeleton on first run
    skeleton   modules/<module>/exercise.py as shipped (must fail)
    reference  the reference brick in assistant/ (must pass)
"""

import contextlib
import datetime
import importlib
import importlib.util
import os
import shutil
import sys
import traceback
from pathlib import Path
from types import ModuleType

from assistant.config import ROOT, settings

PROGRESS_TEMPLATE = """# Progression de {learner}

## Modules validés

## Notes

Ce qui a coincé, les questions ouvertes, les idées de modules.
"""


# Errors caused by the machine setup (model server, credentials, missing dependency group),
# not by the learner's code.
SETUP_ERRORS = ("APIConnectionError", "APITimeoutError", "ConnectError", "NotFoundError", "AuthenticationError", "ModuleNotFoundError")


def require(module: str, command: str) -> None:
    """Stops with an install hint when a module's optional dependencies are missing. Call before importing them."""
    if importlib.util.find_spec(module) is None:
        print(f"Ce module demande des dépendances supplémentaires. Installe-les avec : {command}")
        sys.exit(2)


class Check:
    def __init__(self, check_file: str, reference: str):
        # Windows consoles and pipes do not default to UTF-8.
        for stream in (sys.stdout, sys.stderr):
            stream.reconfigure(encoding="utf-8", errors="replace")
        self.module_dir = Path(check_file).resolve().parent
        self.name = self.module_dir.name
        self.mode = os.environ.get("COURSE_MODE", "learner")
        self.exercise_path: Path | None = None
        print(f"Module {self.name}")
        self.exercise = self._load(reference)

    def _load(self, reference: str) -> ModuleType:
        if self.mode == "reference":
            return importlib.import_module(reference)
        if self.mode == "skeleton":
            self.exercise_path = self.module_dir / "exercise.py"
        else:
            self.exercise_path = self._learner_copy()
        spec = importlib.util.spec_from_file_location(f"exercise_{self.name[:2]}", self.exercise_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as error:
            self._fail("chargement de ton exercice", self._explain(error))
        return module

    def _learner_copy(self) -> Path:
        if not settings.learner:
            print("  Ton prénom n'est pas configuré. Copie .env.example vers .env et renseigne LEARNER=tonprenom.")
            sys.exit(2)
        path = ROOT / "learners" / settings.learner / f"{self.name}.py"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.module_dir / "exercise.py", path)
            print(f"  Ton exercice vient d'être créé : {path.relative_to(ROOT)}")
            print("  Complète-le, puis relance ce check.")
        return path

    @contextlib.contextmanager
    def step(self, label: str):
        try:
            yield
        except NotImplementedError:
            self._fail(label, "cette fonction n'est pas encore écrite.")
        except AssertionError as error:
            self._fail(label, str(error) or "le résultat n'est pas celui attendu.")
        except Exception as error:
            self._fail(label, self._explain(error), blame_exercise=type(error).__name__ not in SETUP_ERRORS)
        else:
            print(f"  [ok] {label}")

    def _explain(self, error: Exception) -> str:
        kind = type(error).__name__
        if kind in ("APIConnectionError", "APITimeoutError", "ConnectError"):
            return (
                f"impossible de joindre le modèle ({settings.chat_base_url}). "
                "Lance Ollama (`ollama serve`) ou vérifie les adresses dans .env."
            )
        if kind == "NotFoundError":
            return (
                f"le modèle demandé est introuvable. En local : `ollama pull {settings.chat_model}` "
                f"et `ollama pull {settings.embed_model}`. Détail : {error}"
            )
        if kind == "AuthenticationError":
            return "la clé d'API est refusée. Vérifie CHAT_API_KEY ou OPENROUTER_API_KEY dans .env."
        if kind == "ModuleNotFoundError":
            return f"{error}. Ce module demande un groupe de dépendances, la commande est en tête de sa leçon."
        return f"{kind} : {error}{self._where(error)}"

    def _where(self, error: Exception) -> str:
        """Line of the exercise file where the error was raised, if any."""
        if not self.exercise_path:
            return ""
        frames = [f for f in traceback.extract_tb(error.__traceback__) if Path(f.filename) == self.exercise_path]
        return f" (ligne {frames[-1].lineno} de ton exercice)" if frames else ""

    def _fail(self, label: str, reason: str, blame_exercise: bool = True) -> None:
        print(f"  [échec] {label}")
        print(f"          {reason}")
        if self.exercise_path and blame_exercise:
            print(f"          Fichier à corriger : {self.exercise_path.relative_to(ROOT)}")
        sys.exit(1)

    def finish(self) -> None:
        print(f"Module {self.name} validé.")
        if self.mode == "learner":
            self._record_progress()

    def _record_progress(self) -> None:
        path = ROOT / "learners" / settings.learner / "progress.md"
        text = path.read_text(encoding="utf-8") if path.exists() else PROGRESS_TEMPLATE.format(learner=settings.learner)
        if f"- {self.name} :" in text:
            return
        line = f"- {self.name} : validé le {datetime.date.today().isoformat()}"
        head, notes_heading, tail = text.partition("\n## Notes")
        head = head.rstrip("\n")
        head += ("\n\n" if head.endswith("validés") else "\n") + line + "\n"
        path.write_text(head + notes_heading + tail, encoding="utf-8")
        print(f"Progression mise à jour : {path.relative_to(ROOT)}")
