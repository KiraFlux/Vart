import sys
from pathlib import Path

sys.stdout = open("out.txt", "wt", encoding="utf-8")

DIR = Path("../lib")

for file in DIR.rglob("*.py"):
    try:
        print(f"{file.relative_to(DIR)}")
        print("```py")
        print(file.read_text(encoding='utf-8', errors='ignore').rstrip())
        print("```\n")
    except:
        pass
