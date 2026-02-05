from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.impl.buttons import CheckBox
from kf_dpg.impl.containers import ChildWindow, HBox, VBox
from kf_dpg.impl.text import Text
from vart.assets import Assets
from vart.misc.log import Logger


class JornalView(CustomWidget):

    def __init__(self) -> None:
        self._text: Final = Text().withFont(Assets.log_font)
        self._channels: Final = VBox()
        self._active_channels: Final = set[str]()

        super().__init__(
            ChildWindow()
            .add(
                HBox()
                .add(
                    VBox()
                    .add(
                        Text("Каналы")
                        .withFont(Assets.title_font)
                    )
                    .add(
                        ChildWindow(
                            _width=300,
                            scrollable_y=True
                        )
                        .add(
                            self._channels
                        )
                    )
                )
                .add(
                    ChildWindow(
                        scrollable_y=True
                    )
                    .add(self._text)
                )
            )
        )

        Logger.on_write.addListener(lambda _: self._onMessage())
        Logger.on_create.addListener(self._createLogWidget)

        for key in Logger.getKeys():
            self._createLogWidget(key)

    def _createLogWidget(self, key: str) -> None:
        self._channels.add(
            CheckBox(
                _value=False,
            )
            .withLabel(key)
            .withHandler(
                lambda state: self._onKeyWidget(key, state)
            )
        )

    def _onKeyWidget(self, key: str, value: bool) -> None:
        if value:
            self._active_channels.add(key)

        else:
            self._active_channels.remove(key)

        self._onMessage()

    def _onMessage(self) -> None:
        self._text.setValue('\n'.join(Logger.getByFilter(tuple(self._active_channels))))
