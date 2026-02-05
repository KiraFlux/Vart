import os
import sys
from pathlib import Path
from typing import Final

project_name: Final = "Vart-Studio-Remastered"


def get_project_dir() -> Path:
    project_dir = Path(os.getcwd())

    if project_dir.name == project_name:
        return project_dir
    else:
        return project_dir.parent


def attach_libs() -> None:
    project_dir = get_project_dir()
    sys.path.extend(
        map(str, (
            i
            for i in (project_dir / "lib").glob("*")
            if i.is_dir()
        ))
    )
