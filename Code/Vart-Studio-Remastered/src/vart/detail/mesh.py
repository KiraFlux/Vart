from typing import Final, Iterable, AbstractSet

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D
from vart.detail.trajectory import Trajectory
from vart.detail.transformation import Transformation
from vart.misc.log import Logger


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


class Mesh:
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
            transformation: Transformation = None
    ):
        self.transformation: Final = transformation or Transformation.default()
        self.trajectories: Final = ObservableRegistry(trajectories)

        self._name = name
        self.on_name_changed: Final = Subject[str]()

    def clone(self) -> Mesh:
        return Mesh(
            trajectories=(
                t.clone()
                for t in self.trajectories.values()
            ),
            name=self._name,
            transformation=self.transformation.clone()
        )

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


class MeshRegistry(ObservableRegistry[Mesh]):

    def add_dummy(self) -> None:
        self.add(Mesh(
            (
                Trajectory(
                    (
                        Vector2D(100, 100),
                        Vector2D(100, -100),
                        Vector2D(-100, -100),
                    ),
                    tool_id=1,
                    is_looped=False
                ),
                Trajectory(
                    (
                        Vector2D(-100, -100),
                        Vector2D(-100, 100),
                        Vector2D(100, 100),
                    ),
                    tool_id=2,
                    is_looped=True
                ),
            ),
            name="Dummy"
        ))

    def add_clone(self, mesh: Mesh) -> None:
        self.add(mesh.clone())

    def remove(self, mesh: Mesh) -> None:
        mesh.trajectories.clear()
        super().remove(mesh)
