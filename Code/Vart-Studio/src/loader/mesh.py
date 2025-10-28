"""Загрузчик OBJ файла"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from itertools import chain
from math import cos
from math import hypot
from math import radians
from math import sin
from pathlib import Path
from typing import Callable
from typing import ClassVar
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import TextIO

from figure.impl.generative import GenerativeFigure
from figure.impl.transformable import TransformableFigure
from figure.impl.transformable import TransformableFigure
from gen.vertex import Vertices
from tools import greedySort
from ui.widgets.abc import ItemID
from ui.widgets.custom.input2d import InputInt2D
from ui.widgets.custom.input3d import InputInt3D
from ui.widgets.dpg.impl import Checkbox
from ui.widgets.dpg.impl import CollapsingHeader
from ui.widgets.dpg.impl import TextInput

type vec2 = tuple[float, float]


@dataclass(frozen=True)
class Vector3D:
    x: float
    y: float
    z: float

    @classmethod
    def fromParts(cls, parts: Iterable[str]) -> Vector3D:
        return cls(*map(float, parts))

    @classmethod
    def avg(cls, v: Sequence[Vector3D]) -> Vector3D:
        _l = len(v)

        return Vector3D(
            sum(n.x for n in v) / _l,
            sum(n.y for n in v) / _l,
            sum(n.z for n in v) / _l,
        )

    def length(self) -> float:
        return hypot(self.x, self.y, self.z)

    def normalized(self) -> Vector3D:
        _l = self.length()
        return Vector3D(self.x / _l, self.y / _l, self.z / _l)

    def dist(self, v: Vector3D) -> float:
        return hypot(self.x - v.x, self.y - v.y, self.z - v.z)

    def add(self, v: Vector3D) -> Vector3D:
        return Vector3D(self.x + v.x, self.y + v.y, self.z + v.z)

    def compMul(self, m: Vector3D) -> Vector3D:
        return Vector3D(self.x * m.x, self.y * m.y, self.z * m.z)

    def rotated_x(self, angle: float) -> Vector3D:
        r = radians(angle)
        c = cos(r)
        s = sin(r)

        return Vector3D(
            self.x,
            self.y * c - self.z * s,
            self.y * s + self.z * c
        )

    def rotated_y(self, angle: float) -> Vector3D:
        r = radians(angle)
        c = cos(r)
        s = sin(r)

        return Vector3D(
            self.x * c + self.z * s,
            self.y,
            -self.x * s + self.z * c
        )

    def dot(self, v: Vector3D) -> float:
        return self.x * v.x + self.y * v.y + self.z * v.z


class Projector(ABC):
    """Проектор"""

    _cameraVertex: ClassVar = Vector3D(-1, 1, -1)

    @abstractmethod
    def project(self, v: Vector3D) -> tuple[float, float]:
        """Спроецировать вектор на дисплей"""

    def isVisible(self, n: Vector3D) -> bool:
        return self._cameraVertex.dot(n) >= 0


class IsometricProjector(Projector):

    def project(self, v: Vector3D) -> tuple[float, float]:
        return (
            (v.x - v.z) * cos(radians(30)),
            (v.x + v.z) * sin(radians(30)) + v.y
        )


@dataclass
class _Mesh:
    name: str
    vertices: list[Vector3D]


@dataclass
class _MeshFace:
    _cameraVertex: ClassVar = Vector3D(-1, 1, -1)

    vertices: list[Vector3D]
    normal: Vector3D
    centroid: Vector3D

    @classmethod
    def parse(cls, parts: Iterable[str], model: _AdvancedMesh, v_offset: int, n_offset: int) -> _MeshFace:
        vertices = list()
        normals = list()

        for part in parts:
            v, _, n = part.split('/')

            v_index = int(v) - v_offset
            vertices.append(model.vertices[v_index])

            n_index = int(n) - n_offset
            normals.append(model.normals[n_index])

        vertices.append(vertices[0])

        return cls(vertices, Vector3D.avg(normals), Vector3D.avg(vertices))


@dataclass
class _AdvancedMesh(_Mesh):
    normals: list[Vector3D]
    faces: list[_MeshFace]

    @classmethod
    def load(cls, path: Path) -> Sequence[_AdvancedMesh]:
        with open(path) as f:
            return cls._loadFromObj(f)

    @classmethod
    def _loadFromObj(cls, stream: TextIO) -> Sequence[_AdvancedMesh]:
        def err(msg: str) -> None:
            """err"""
            raise ValueError(f"Err : {cls.__name__} : ( '{stream}' ) : {msg}")

        objects = list[_AdvancedMesh]()
        current_model: Optional[_AdvancedMesh] = None

        v_index_offset = 1
        n_index_offset = 1

        for index, line in enumerate(stream):
            parts = line.strip().split()

            if not parts:
                continue

            match parts[0]:
                case 'o':
                    if current_model is not None:
                        v_index_offset += len(current_model.vertices)
                        n_index_offset += len(current_model.normals)

                    current_model = _AdvancedMesh(parts[1], list(), list(), list())
                    objects.append(current_model)

                case 'v':
                    if current_model is None:
                        err(f"obj not selected (v) - at {index}")

                    current_model.vertices.append(Vector3D.fromParts(parts[1:4]))

                case 'vn':
                    if current_model is None:
                        err(f"obj not selected (n) at {index}")

                    current_model.normals.append(Vector3D.fromParts(parts[1:4]))

                case 'f':
                    if current_model is None:
                        err(f"obj not selected (f) at {index}")

                    face = _MeshFace.parse(parts[1:], current_model, v_index_offset, n_index_offset)

                    current_model.faces.append(face)

        return objects


class TextMeshFigure(GenerativeFigure):

    def __init__(self, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> None:
        super().__init__("text", on_delete, on_clone)

        self._text = TextInput()
        pass

    def setText(self, text: str) -> None:
        self._text.setValue(text)

    def getText(self) -> str:
        return self._text.getValue()

    def _generateVertices(self) -> Vertices:
        pass


class LegacyMeshFigure(GenerativeFigure):

    @classmethod
    def load(cls, path: Path, on_delete: Callable, on_clone: Callable) -> Iterable[LegacyMeshFigure]:
        return (LegacyMeshFigure(m.name, on_delete, on_clone, m) for m in (_AdvancedMesh.load(path)))

    def __init__(self, label: str, on_delete: Callable, on_clone: Callable, model: _AdvancedMesh) -> None:
        super().__init__(label, on_delete, on_clone)

        self._model = model
        self._isometric_projector = IsometricProjector()

        update_ = lambda _: self.update()

        self._rotation_XY = InputInt2D(
            "Поворот 2D",
            update_,
            value_range=(-360, 360),
            step_fast=5,
            reset_button=True,
            is_horizontal=True
        )

        self._scale_XYZ = InputInt3D(
            "Масштаб",
            update_,
            (-500, 500),
            reset_button=True,
            default_value=(100, 100, 100)
        )

        self._use_beta_gen = Checkbox(update_, label="Отрисовка 2", default_value=False)
        self._face_culling = Checkbox(update_, label="Отсечение невидимых граней", default_value=True)

    def _getCloneInstance(self, name: str, on_delete: Callable, on_clone: Callable) -> LegacyMeshFigure:
        return LegacyMeshFigure(name, on_delete, on_clone, self._model)

    def getMeshScaleXYZ(self) -> Vector3D:
        x, y, z = self._scale_XYZ.getValue()
        return Vector3D(x / 100, y / 100, z / 100)

    def _vertexTransform(self, v: Vector3D) -> Vector3D:
        rx, ry = self._rotation_XY.getValue()
        return v.compMul(self.getMeshScaleXYZ()).rotated_y(ry).rotated_x(rx)

    def _getProjector(self) -> Projector:
        return self._isometric_projector

    def _generateVertices(self) -> Vertices:
        return self._draw1()

    def _draw1(self) -> Vertices:
        projector = self._getProjector()

        # определение видимых граней
        def _getVisibleFaces() -> Iterable[_MeshFace]:
            if self._face_culling.getValue():
                return (f for f in self._model.faces if projector.isVisible(self._vertexTransform(f.normal)))

            return self._model.faces

        visible_faces = _getVisibleFaces()

        # проецирование граней
        def project_face(f: _MeshFace) -> Sequence[vec2]:
            return tuple(map(projector.project, map(self._vertexTransform, f.vertices)))

        projections = tuple(map(project_face, visible_faces))

        # сортировка проекций
        def _metric(a: Sequence[vec2], b: Sequence[vec2]) -> float:
            ax, ay = _centroid(a)
            bx, by = _centroid(b)

            return hypot(ax - bx, ay - by)

        def _centroid(__v: Sequence[vec2]) -> vec2:
            _x, _y = zip(*__v)
            _l = len(__v)
            return sum(_x) / _l, sum(_y) / _l

        projections_sorted = greedySort(projections, _metric)

        # комбинирование TODO решение общих ребер
        combined = chain(*projections_sorted)

        return zip(*combined)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        (
            CollapsingHeader("Трансформации 3D", default_open=True).place(self)
            .add(self._rotation_XY)
            .add(self._face_culling)
            .add(self._scale_XYZ)
        )
