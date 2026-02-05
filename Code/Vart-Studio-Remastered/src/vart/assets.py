from pathlib import Path
from typing import Final, final

import vart.boot
from kf_dpg.core.dpg.font import DpgFont


@final
class Assets:

    @staticmethod
    def app_path() -> Path:
        return vart.boot.get_project_dir()

    assets_dir: Final = app_path() / "assets"

    fonts_dir: Final = assets_dir / "fonts"

    default_font: Final = DpgFont(fonts_dir / r"JetBrainsMono.ttf", 20)

    log_font: Final = default_font.sub(size=16)

    label_font: Final = default_font.sub(size=32)

    title_font: Final = DpgFont(fonts_dir / r"Library3am-5V3Z.otf", 48)

    def __new__(cls):
        raise TypeError
