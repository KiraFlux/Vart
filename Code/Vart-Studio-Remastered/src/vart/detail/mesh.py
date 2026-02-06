from typing import Sequence, Final, Iterable

from kf_dpg.misc.subject import Subject
from kf_dpg.misc.vector import Vector2D
from vart.misc.log import Logger


class Mesh2D:
    """
    2D меш
    """

    type vec2f = Vector2D[float]

    @classmethod
    def from_text_repr(cls, text: str) -> tuple[Sequence[vec2f], Sequence[int]]:
        vertices = list[Vector2D[float]]()
        indices = list[int]()

        in_trajectory = False
        vertex_index = 0

        for line in text.splitlines():
            line = line.strip()

            if line:
                if not in_trajectory:
                    indices.append(vertex_index)

                parts = line.split()
                if len(parts) == 2:
                    x, y = map(float, parts)
                    vertices.append(Vector2D(x, y))
                    vertex_index += 1
                    in_trajectory = True

            else:
                in_trajectory = False

        return vertices, indices

    def to_text_repr(self) -> str:
        """
        Преобразовать меш в текстовое представление
        Формат: вершины по строкам, траектории разделяются пустыми строками
        """
        if not self._vertices:
            return ""

        lines = []
        indices = sorted(set(self._trajectory_start_indices))

        for i in range(len(indices)):
            start = indices[i]
            end = indices[i + 1] if i + 1 < len(indices) else len(self._vertices)

            for j in range(start, end):
                vertex = self._vertices[j]
                lines.append(f"{vertex.x} {vertex.y}")

            if i < len(indices) - 1:
                lines.append("")

        if lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def __init__(
            self,
            vertices: Sequence[vec2f],
            trajectory_start_indices: Sequence[int],
            *,
            tool_index: int = 1,  # 0 - disable
            name: str = None,
            scale: vec2f = Vector2D(1, 1),
            rotation: float = 0,
            translation: vec2f = Vector2D(0, 0),
    ) -> None:
        self.on_change: Final[Subject[Mesh2D]] = Subject()
        self._vertices = vertices
        self._trajectory_start_indices = trajectory_start_indices

        self._rotation = rotation
        self._scale = scale
        self._translation = translation

        self._name = name or str(self)
        self._tool_index = tool_index

    @property
    def tool_index(self):
        """
        Инструмент
        0 - не участвует в печати
        1, 2, i, ... - использовать i-й инструмент
        """
        return self._tool_index

    def set_tool_index(self, tool_index: str):
        if self._tool_index != tool_index:
            self._tool_index = tool_index
            self.on_change.notify(self)

    @tool_index.setter
    def tool_index(self, n):
        self.set_tool_index(n)

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
    def trajectory_start_indices(self):
        """Индексы начальных вершин траекторий"""
        return self._trajectory_start_indices

    def set_trajectory_start_indices(self, indices: Sequence[int]):
        if self._trajectory_start_indices != indices:
            self._trajectory_start_indices = indices
            self.on_change.notify(self)

    @trajectory_start_indices.setter
    def trajectory_start_indices(self, i):
        self.set_trajectory_start_indices(i)

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

    def __str__(self):
        return f"<{self.__class__.__name__}@{id(self)}>"

    def __repr__(self):
        return (
                f"<{self.__class__.__name__}@{id(self)} " +
                f"v:{len(self._vertices)} " +
                f"i:{len(self._trajectory_start_indices)} " +
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
        self._log.write(f"add: {mesh!r}")
        self._items.add(mesh)
        self.on_add.notify(mesh)

    def remove(self, mesh: Mesh2D) -> None:
        self._log.write(f"remove: {mesh!r}")
        self._items.remove(mesh)
        self.on_remove.notify(mesh)

    def clear(self) -> None:
        self._log.write(f"clear")

        for mesh in tuple(self._items):
            self.remove(mesh)

        self._items.clear()

    def get_all(self) -> Iterable[Mesh2D]:
        return self._items

    def items_count(self) -> int:
        return len(self._items)


def _test():
    s = """1 1
    
2 2
3 3


4 4
5 5
6 6






"""

    v, i = Mesh2D.from_text_repr(s)
    print(v, i)

    m = Mesh2D(v, i)

    print(m.to_text_repr())

    pass


if __name__ == '__main__':
    _test()
