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
            tool_id: int = 1,
            is_looped: bool = False
    ):
        self.on_geometry_change: Final[Subject[Trajectory]] = Subject()
        self.on_tool_id_change: Final[Subject[int]] = Subject()

        self._vertices = vertices
        self._tool_id = tool_id
        self._is_looped = is_looped

    def clone(self) -> Trajectory:
        return Trajectory(
            self._vertices,
            tool_id=self._tool_id,
            is_looped=self._is_looped
        )

    def transformed(self, transformation: Callable[[vec2f], tuple[float, float]]) -> tuple[list[float], list[float]]:
        result_x = list()
        result_y = list()

        for vertex in self.vertices:
            x, y = transformation(vertex)
            result_x.append(x)
            result_y.append(y)

        if self._is_looped:
            result_x.append(result_x[0])
            result_y.append(result_y[0])

        return result_x, result_y

    @property
    def vertices(self):
        """Вершины (x, y) в каноничном базисе"""
        return self._vertices

    def set_vertices(self, v: Sequence[vec2f]):
        if self._vertices != v:
            self._vertices = v
            self.on_geometry_change.notify(self)

    @vertices.setter
    def vertices(self, v):
        self.set_vertices(v)

    @property
    def tool_id(self):
        """
        Выбранный идентификатор инструмента
        0 - Инструмент не выбран
        """
        return self._tool_id

    def set_tool_id(self, tool_id: int):
        if self._tool_id != tool_id:
            self._tool_id = tool_id
            self.on_tool_id_change.notify(tool_id)

    @tool_id.setter
    def tool_id(self, i):
        self.set_tool_id(i)

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
            self.on_geometry_change.notify(self)
