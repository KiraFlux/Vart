from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import ClassVar

from trajex.vector3d import Vector3D


class Projector(ABC):
    """Проектор"""

    _cameraVertex: ClassVar = Vector3D(-1, 1, -1)

    @abstractmethod
    def project(self, v: Vector3D) -> tuple[float, float]:
        """Спроецировать вектор на дисплей"""

    def is_visible(self, n: Vector3D) -> bool:
        return self._cameraVertex.dot(n) >= 0


class IsometricProjector(Projector):

    def project(self, v: Vector3D) -> tuple[float, float]:
        return (
            (v.x - v.z) * math.cos(math.radians(30)),
            (v.x + v.z) * math.sin(math.radians(30)) + v.y
        )
