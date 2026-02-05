from kf_dpg.core.custom import CustomWidget
from kf_dpg.impl.containers import VBox


class ConfigView(CustomWidget):
    def __init__(self) -> None:
        super().__init__(
            VBox()
        )
