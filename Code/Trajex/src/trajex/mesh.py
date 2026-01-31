"""Загрузчик OBJ файла"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import TextIO

from trajex.vector3d import Vector3D


@dataclass
class Mesh:
    name: str
    vertices: list[Vector3D]


@dataclass
class MeshFace:
    _cameraVertex: ClassVar = Vector3D(-1, 1, -1)

    vertices: list[Vector3D]
    normal: Vector3D
    centroid: Vector3D

    @classmethod
    def parse(cls, parts: Iterable[str], model: AdvancedMesh, v_offset: int, n_offset: int) -> MeshFace:
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
class AdvancedMesh(Mesh):
    normals: list[Vector3D]
    faces: list[MeshFace]

    @classmethod
    def parse(cls, stream: TextIO) -> Sequence[AdvancedMesh]:
        def __err(msg: str) -> None:
            raise ValueError(f"Err : {cls.__name__} : ( '{stream}' ) : {msg}")

        objects = list[AdvancedMesh]()
        current_model: Optional[AdvancedMesh] = None

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

                    current_model = AdvancedMesh(parts[1], list(), list(), list())
                    objects.append(current_model)

                case 'v':
                    if current_model is None:
                        __err(f"obj not selected (v) - at {index}")

                    current_model.vertices.append(Vector3D.from_parts(parts[1:4]))

                case 'vn':
                    if current_model is None:
                        __err(f"obj not selected (n) at {index}")

                    current_model.normals.append(Vector3D.from_parts(parts[1:4]))

                case 'f':
                    if current_model is None:
                        __err(f"obj not selected (f) at {index}")

                    face = MeshFace.parse(parts[1:], current_model, v_index_offset, n_index_offset)

                    current_model.faces.append(face)

        return objects
