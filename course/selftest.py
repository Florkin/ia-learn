"""Replays every module's check twice: on the shipped skeleton (must fail) and on the reference (must pass).

Usage: uv run --all-groups python -m course.selftest [module-prefix ...]
"""

import os
import subprocess
import sys

from assistant.config import ROOT


def run(check: str, mode: str) -> tuple[int, str]:
    env = {**os.environ, "COURSE_MODE": mode}
    result = subprocess.run([sys.executable, check], env=env, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout + result.stderr


def main(prefixes: list[str]) -> int:
    modules = sorted(d for d in (ROOT / "modules").iterdir() if (d / "check.py").exists())
    if prefixes:
        modules = [d for d in modules if d.name.startswith(tuple(prefixes))]
    failures = 0
    for module in modules:
        check = str(module / "check.py")
        skeleton_code, skeleton_out = run(check, "skeleton")
        reference_code, reference_out = run(check, "reference")
        # The skeleton must fail on a check step (exit 1), not crash.
        ok = skeleton_code == 1 and reference_code == 0
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {module.name:28s} skeleton exit={skeleton_code} reference exit={reference_code}")
        if not ok:
            print((reference_out if reference_code else skeleton_out).rstrip())
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
