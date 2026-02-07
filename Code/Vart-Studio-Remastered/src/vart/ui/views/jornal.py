from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.impl.buttons import CheckBox, Button
from kf_dpg.impl.containers import ChildWindow, HBox, VBox
from kf_dpg.impl.text import Text
from vart.assets import Assets
from vart.misc.log import Logger


class JornalView(CustomWidget):

    def __init__(self) -> None:
        self._text: Final = Text()
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
                        .with_font(Assets.title_font)
                    )
                    .add(
                        ChildWindow(
                            _width=300,
                            scrollable_y=True
                        )
                        .add(
                            Button()
                            .with_width(-1)
                            .with_label("Очистить")
                            .with_handler(self._clear)
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
                    .add(
                        self._text
                        .with_font(Assets.log_font)
                    )
                )
            )
        )

        Logger.on_write.add_listener(lambda _: self._on_message())
        Logger.on_create.add_listener(self._create_log_widget)

        for key in Logger.get_keys():
            self._create_log_widget(key)

    def _clear(self):
        Logger.clear()
        self._on_message()

    def _create_log_widget(self, key: str) -> None:
        self._channels.add(
            CheckBox(
                _value=False,
            )
            .with_label(key)
            .with_handler(
                lambda state: self._on_key_widget(key, state)
            )
        )

    def _on_key_widget(self, key: str, value: bool) -> None:
        if value:
            self._active_channels.add(key)

        else:
            self._active_channels.remove(key)

        self._on_message()

    def _on_message(self) -> None:
        self._text.set_value('\n'.join(Logger.get_by_filter(tuple(self._active_channels))))
