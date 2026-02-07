from typing import Final, Iterable, AbstractSet

from kf_dpg.misc.subject import Subject
from vart.detail.trajectory import Trajectory
from vart.detail.transformation import Transformation2D
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

    def clone(self) -> Mesh2D:
        return Mesh2D(
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


class MeshRegistry(ObservableRegistry[Mesh2D]):

    def add_clone(self, mesh: Mesh2D) -> None:
        self.add(mesh.clone())

    def remove(self, mesh: Mesh2D) -> None:
        mesh.trajectories.clear()
        super().remove(mesh)
