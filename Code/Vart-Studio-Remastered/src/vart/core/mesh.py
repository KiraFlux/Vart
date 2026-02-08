import math
from typing import Final, Iterable

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D
from vart.core.trajectory import Trajectory
from vart.core.transformation import Transformation
from vart.misc.observable import ObservableRegistry


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

        self._clone_count: int = 0

    def extract_trajectory(self, trajectory: Trajectory) -> Mesh:
        self.trajectories.remove(trajectory)
        return Mesh(
            trajectories=(
                trajectory,
            ),
            name=f"{self._name} - T:{len(trajectory.vertices)}",
            transformation=self.transformation.clone()
        )

    def clone(self) -> Mesh:
        self._clone_count += 1
        return Mesh(
            trajectories=(
                t.clone()
                for t in self.trajectories.values()
            ),
            name=f"{self._name} ({self._clone_count})",
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

    def add_extracted_trajectory(self, mesh: Mesh, trajectory: Trajectory) -> None:
        self.add(mesh.extract_trajectory(trajectory))

    def add_clone(self, mesh: Mesh) -> None:
        self.add(mesh.clone())

    def add_circle(
            self,
            segments: int,
            radius: float,
    ):
        pi_segments = 2 * math.pi / segments

        self.add(Mesh(
            trajectories=(
                Trajectory(
                    tuple(
                        Vector2D(radius * math.cos(angle), radius * math.sin(angle))
                        for angle in map(
                            lambda i: i * pi_segments,
                            range(segments)
                        )
                    ),
                    name=f"circle: {radius=} {segments=}",
                    is_looped=True
                ),
            )
        ))

    def add_dummy(self):
        self.add(Mesh(
            (
                Trajectory(
                    (
                        Vector2D(50, 50),
                        Vector2D(100, -100),
                        Vector2D(-50, -50),
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
            name=f"Dummy:{len(self._items)}"
        ))

    def remove(self, mesh: Mesh) -> None:
        mesh.trajectories.clear()
        super().remove(mesh)
