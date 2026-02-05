from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.impl.boxes import TextInput
from kf_dpg.impl.containers import VBox
from vart.assets import Assets
from vart.misc.log import Logger


class PreparingView(CustomWidget):
    def __init__(self) -> None:
        super().__init__(
            VBox()
            .add(
                TextInput(
                    default="Preparing | Подготовка"
                )
                .withFont(
                    Assets.title_font
                )
            )
        )

        self._log: Final = Logger(self.__class__.__name__)
