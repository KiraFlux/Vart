from typing import Sequence, Final, Callable

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D


class Trajectory:
    """
    Траектория
    Неразрывная линия одного цвета
    """

    type vec2f = Vector2D[float]

    def __init__(
            self,
            vertices: Sequence[vec2f],
            *,
            is_looped: bool = False
    ):
        self.on_change: Final[Subject[Trajectory]] = Subject()

        self._vertices = vertices
        self._is_looped = is_looped

    def clone(self) -> Trajectory:
        return Trajectory(
            self._vertices,
            is_looped=self._is_looped
        )

    def transformed(self, transformation: Callable[[vec2f], tuple[float, float]]) -> tuple[list[float], list[float]]:
        result_x = list()
        result_y = list()

        for vertex in self.vertices:
            x, y = transformation(vertex)
            result_x.append(x)
            result_y.append(y)

        return result_x, result_y

    @property
    def vertices(self):
        """Вершины (x, y) в каноничном базисе"""
        return self._vertices

    def set_vertices(self, v: Sequence[vec2f]):
        if self._vertices != v:
            self._vertices = v
            self.on_change.notify(self)

    @vertices.setter
    def vertices(self, v):
        self.set_vertices(v)

    @property
    def is_looped(self):
        """
        Замкнутость траектории
        Конечная вершина переходит к начальной
        """
        return self._is_looped

    @is_looped.setter
    def is_looped(self, x):
        if self._is_looped != x:
            self._is_looped = x
            self.on_change.notify(self)
