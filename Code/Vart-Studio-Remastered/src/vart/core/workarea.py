from typing import Final

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D


class WorkArea:
    type vec2f = Vector2D[float]

    def __init__(
            self, *,
            width: float,
            height: float,
    ):
        self.on_width_changed: Final = Subject[float]()
        self.on_height_changed: Final = Subject[float]()

        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        """Ширина рабочей области"""
        return self._width

    def set_width(self, width: float):
        if self._width != width:
            width = max(0.0, width)
            self._width = width
            self.on_width_changed.notify(width)

    @width.setter
    def width(self, w):
        self.set_width(w)

    @property
    def height(self) -> float:
        """Высота рабочей области"""
        return self._height

    def set_height(self, height: float):
        if self._height != height:
            height = max(0.0, height)
            self._height = height
            self.on_height_changed.notify(height)

    @height.setter
    def height(self, w):
        self.set_height(w)
