from typing import Sequence, Final, Iterable, AbstractSet

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D
from vart.misc.log import Logger

type vec2f = Vector2D[float]


class Transformation2D:

    @classmethod
    def default(cls) -> Transformation2D:
        return cls(
            scale=Vector2D(1, 1),
            rotation=0,
            translation=Vector2D(0, 0)
        )

    def __init__(self, *, scale: vec2f, rotation: float, translation: vec2f):
        self.on_change: Final[Subject[Transformation2D]] = Subject()

        self._rotation = rotation
        self._scale = scale
        self._translation = translation

    def __repr__(self):
        return f"<{self.__class__.__name__} S:{self._scale} R:{self._rotation} T:{self._translation}>"

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


class Trajectory:
    """
    Траектория
    Неразрывная линия одного цвета
    """

    def __init__(
            self,
            vertices: Sequence[vec2f],
            *,
            is_looped: bool = False
    ):
        self.on_change: Final[Subject[Trajectory]] = Subject()

        self._vertices = vertices
        self._is_looped = is_looped

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


class ObservableRegistry[T]:

    def __init__(self, init: Iterable[T] = ()):
        self.on_add: Final = Subject[T]()
        self.on_remove: Final = Subject[T]()
        self._items: Final = set[T](init)

        self._log: Final = Logger(f"{self.__class__.__name__}@{id(self)}")

    def add(self, item: T) -> None:
        self._log.write(f"add: {item!r}")
        self._items.add(item)
        self.on_add.notify(item)

    def remove(self, item: T) -> None:
        self._log.write(f"remove: {item!r}")
        self._items.remove(item)
        self.on_remove.notify(item)

    def clear(self) -> None:
        self._log.write(f"clear")

        for item in tuple(self._items):
            self.remove(item)

        self._items.clear()

    def values(self) -> AbstractSet[T]:
        return self._items


class Mesh2D:
    """
    2D меш
    Группа траекторий.
    Имеет общую трансформацию
    """

    def __init__(
            self,
            trajectories: Iterable[Trajectory],
            *,
            name: str = "unnamed",
            transformation: Transformation2D = None
    ):
        self.transformation: Final = transformation or Transformation2D.default()
        self.trajectories: Final = ObservableRegistry(trajectories)

        self._name = name
        self.on_name_changed: Final = Subject[str]()

    @property
    def name(self):
        """Наименование (Отладка)"""
        return self._name

    def set_name(self, name: str):
        if self._name != name:
            self._name = name
            self.on_name_changed.notify(name)

    @name.setter
    def name(self, n):
        self.set_name(n)

    def __str__(self):
        return f"<{self.__class__.__name__}@{id(self)}>"

    def __repr__(self):
        return (
                f"<{self.__class__.__name__}@{id(self)} " +
                f"t:{self.transformation} " +
                f"{self.trajectories.values()}"
                ">"
        )


class MeshRegistry(ObservableRegistry[Mesh2D]):

    def remove(self, mesh: Mesh2D) -> None:
        mesh.trajectories.clear()
        super().remove(mesh)
