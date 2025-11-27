import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAT_QWIDGET_NOARGS = re.compile(r"\bQWidget\s*\(\s*\)")
PAT_SUPER_INIT_NOARG = re.compile(r"super\(\s*\)\s*\.\s*__init__\s*\(\s*\)")
ignore_dirs = {".venv", "__pycache__", "build", ".git", "tools"}


def scan():
    problems = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue

            path = os.path.join(dirpath, fn)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if PAT_QWIDGET_NOARGS.search(line):
                            problems.append((path, i, line.strip()))

                        if PAT_SUPER_INIT_NOARG.search(line):
                            problems.append((path, i, line.strip()))

            except Exception as e:
                print(f"ERRO lendo {path}: {e}", file=sys.stderr)

    return problems


if __name__ == "__main__":
    for p in scan():
        print(f"{p[0]}:{p[1]}: {p[2]}")

    if not scan():
        print("Nenhuma ocorrência potencial encontrada.")
