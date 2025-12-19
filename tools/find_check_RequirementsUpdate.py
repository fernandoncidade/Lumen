import re
import subprocess
import sys
from pathlib import Path

REQ_FILE = Path(__file__).parent / "requirements.txt"

def parse_name(line: str) -> str | None:
    line = line.split("#", 1)[0].strip()
    if not line:
        return None

    if "://" in line or "@" in line or line.endswith(".whl"):
        return None

    parts = re.split(r'[\s=<>!~@#]+', line)
    return parts[0] if parts else None

def main():
    if not REQ_FILE.exists():
        print(f"Arquivo não encontrado: {REQ_FILE}")
        return 1

    with REQ_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for raw in lines:
        name = parse_name(raw)
        if not name:
            continue

        print(f">> {name}")
        cmd = [sys.executable, "-m", "pip", "index", "versions", name]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out = proc.stdout.strip()
            err = proc.stderr.strip()

            if out:
                print(out)

            if err:
                print(err)

        except Exception as e:
            print(f"Erro ao rodar pip para {name}: {e}")

if __name__ == "__main__":
    sys.exit(main())
