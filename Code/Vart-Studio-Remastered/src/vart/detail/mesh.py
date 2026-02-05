from typing import Sequence, Final, Iterable

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D
from vart.misc.log import Logger


class Mesh2D:
    """
    2D меш
    """

    type vec2f = Vector2D[float]

    def __init__(
            self,
            vertices: Sequence[vec2f],
            trajectory_end_indices: Sequence[int],
            *,
            name: str = None,
            scale: vec2f = Vector2D(1, 1),
            rotation: float = 0,
            translation: vec2f = Vector2D(0, 0),
    ) -> None:
        self.on_change: Final[Subject[Mesh2D]] = Subject()
        self._vertices = vertices
        self._trajectory_end_indices = trajectory_end_indices

        self._rotation = rotation
        self._scale = scale
        self._translation = translation

        self._name = name or repr(self)

    @property
    def name(self):
        """Наименование"""
        return self._name

    def set_name(self, name: str):
        if self._name != name:
            self._name = name
            self.on_change.notify(self)

    @name.setter
    def name(self, n):
        self.set_name(n)

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
    def trajectory_end_indices(self):
        """Индексы конечных вершин траекторий"""
        return self._trajectory_end_indices

    def set_trajectory_end_indices(self, indices: Sequence[int]):
        if self._trajectory_end_indices != indices:
            self._trajectory_end_indices = indices
            self.on_change.notify(self)

    @trajectory_end_indices.setter
    def trajectory_end_indices(self, i):
        self.set_trajectory_end_indices(i)

    @property
    def rotation(self):
        """Поворот в радианах"""
        return self._rotation

    def set_rotation(self, x: float):
        if self._rotation != x:
            self._rotation = x
            self.on_change.notify(self)

    @rotation.setter
    def rotation(self, x):
        self.set_rotation(x)

    @property
    def translation(self):
        """Вектор переноса"""
        return self._translation

    def set_translation(self, x: vec2f):
        if self._translation != x:
            self._translation = x
            self.on_change.notify(self)

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
            self.on_change.notify(self)

    @scale.setter
    def scale(self, x):
        self.set_scale(x)

    def __repr__(self):
        return (
                f"<{self.__class__.__name__}@{id(self)} " +
                f"v:{len(self._vertices)} " +
                f"i:{len(self._trajectory_end_indices)} " +
                f"r:{self._rotation} " +
                f"s:{self._scale} " +
                f"t:{self._translation}" +
                ">"
        )


class MeshRegistry:
    """
    Mesh Реестр
    """

    def __init__(self) -> None:
        self.on_add: Final[Subject[Mesh2D]] = Subject()
        self.on_remove: Final[Subject[Mesh2D]] = Subject()

        self._log: Final = Logger(self.__class__.__name__)
        self._items: Final = set[Mesh2D]()

    def add(self, mesh: Mesh2D) -> None:
        self._log.write(f"add: {mesh}")
        self._items.add(mesh)
        self.on_add.notify(mesh)

    def remove(self, mesh: Mesh2D) -> None:
        self._log.write(f"remove: {mesh}")
        self._items.remove(mesh)
        self.on_remove.notify(mesh)

    def get_all(self) -> Iterable[Mesh2D]:
        return self._items
