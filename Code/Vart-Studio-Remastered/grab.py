import sys
from pathlib import Path

sys.stdout = open("out.txt", "wt", encoding="utf-8")


def _do(p: str):
    d = Path(p)

    for file in d.rglob("*.py"):
        try:
            print(f"{file.relative_to(d)}")
            print(f"```{file.suffix}")
            print(file.read_text(encoding='utf-8', errors='ignore').rstrip())
            print("```\n")
        except:
            pass


_do("./lib")
_do("./src")
