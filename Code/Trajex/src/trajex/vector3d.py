import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Vector3D:
    x: float
    y: float
    z: float

    @classmethod
    def from_parts(cls, parts: Iterable[str]) -> Vector3D:
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
        return math.hypot(self.x, self.y, self.z)

    def normalized(self) -> Vector3D:
        _l = self.length()
        return Vector3D(self.x / _l, self.y / _l, self.z / _l)

    def dist(self, v: Vector3D) -> float:
        return math.hypot(self.x - v.x, self.y - v.y, self.z - v.z)

    def add(self, v: Vector3D) -> Vector3D:
        return Vector3D(self.x + v.x, self.y + v.y, self.z + v.z)

    def comp_mul(self, m: Vector3D) -> Vector3D:
        return Vector3D(self.x * m.x, self.y * m.y, self.z * m.z)

    def rotated_x(self, angle: float) -> Vector3D:
        r = math.radians(angle)
        c = math.cos(r)
        s = math.sin(r)

        return Vector3D(
            self.x,
            self.y * c - self.z * s,
            self.y * s + self.z * c
        )

    def rotated_y(self, angle: float) -> Vector3D:
        r = math.radians(angle)
        c = math.cos(r)
        s = math.sin(r)

        return Vector3D(
            self.x * c + self.z * s,
            self.y,
            -self.x * s + self.z * c
        )

    def dot(self, v: Vector3D) -> float:
        return self.x * v.x + self.y * v.y + self.z * v.z
