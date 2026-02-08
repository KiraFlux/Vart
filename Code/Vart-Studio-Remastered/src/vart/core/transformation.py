import math
from typing import Final

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D


class Transformation:
    type vec2f = Vector2D[float]

    @classmethod
    def default(cls) -> Transformation:
        return cls(
            scale=Vector2D(1, 1),
            rotation=0,
            translation=Vector2D(0, 0)
        )

    def __init__(self, *, scale: vec2f, rotation: float, translation: vec2f):
        self.on_change: Final[Subject[Transformation]] = Subject()

        self._scale = scale
        self._rotation = rotation
        self._translation = translation

    def __repr__(self):
        return f"<{self.__class__.__name__} S:{self._scale} R:{self._rotation} T:{self._translation}>"

    def clone(self) -> Transformation:
        return Transformation(
            scale=self._scale.clone(),
            rotation=self._rotation,
            translation=self._translation.clone()
        )

    def apply(self, point: vec2f) -> tuple[float, float]:
        """
        Применить
        scale, rotation, transpose
        """

        px, py = point.toTuple()

        px *= self._scale.x
        py *= self._scale.y

        sin_a = math.sin(self._rotation)
        cos_a = math.cos(self._rotation)

        rotated_x = px * cos_a - py * sin_a
        rotated_y = px * sin_a + py * cos_a

        return (
            rotated_x + self._translation.x,
            rotated_y + self._translation.y,
        )

    def _on_change(self):
        self.on_change.notify(self)

    @property
    def rotation(self):
        """Поворот в радианах"""
        return self._rotation

    def set_rotation(self, rad: float):
        if self._rotation != rad:
            self._rotation = rad
            self._on_change()

    def get_rotation_degrees(self) -> float:
        return math.degrees(self._rotation)

    def set_rotation_degrees(self, degrees: float):
        self.set_rotation(math.radians(degrees))

    @rotation.setter
    def rotation(self, rad: float):
        self.set_rotation(rad)

    @property
    def translation(self):
        """Вектор переноса"""
        return self._translation

    def set_translation(self, x: vec2f):
        if self._translation != x:
            self._translation = x
            self._on_change()

    @translation.setter
    def translation(self, x):
        self.set_translation(x)

    @property
    def scale(self):
        """Масштабирование по осям в каноничном базисе"""
        return self._scale

    def set_scale(self, x: vec2f):
        if self._scale != x:
            self._scale = x
            self._on_change()

    @scale.setter
    def scale(self, x):
        self.set_scale(x)
