from typing import Sequence

from kf_dpg.core.app import App
from kf_dpg.core.custom import CustomWidget
from kf_dpg.impl.containers import Window, TabBar, Tab
from vart.assets import Assets


class VartApplication(App):
    def __init__(
            self,
            window: Window,
            views: Sequence[tuple[str, CustomWidget]]
    ):
        tab_bar = TabBar()

        for name, view in views:
            tab_bar.add(
                Tab(name)
                .add(view)
            )

        super().__init__(
            window
            .withFont(Assets.default_font)
            .add(tab_bar)
        )
