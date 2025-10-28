import math
from itertools import chain
from itertools import pairwise
from math import cos
from math import pi
from math import radians
from math import sin
from typing import Final
from typing import Iterable

from tools import Range

Vertices = tuple[Iterable[float], Iterable[float]]

type Number = int | float
type Vec2D[T] = tuple[T, T]
Vec2f = Vec2D[float]
Vec2i = Vec2D[int]


class VertexGenerator:
    RESOLUTION_RANGE: Final[Range[int]] = Range(1, 1000)
    POLYGON_VERTEX_COUNT_RANGE: Final[Range[int]] = Range(3, 20)
    SPIRAL_REPEATS: Final[Range[int]] = Range(1, 50)

    @classmethod
    def inflate(cls, v: Vertices, factor: float) -> Vertices:
        """Вздуть вершины"""

        def __transform(__v: Vec2f) -> Vec2f:
            x, y = __v
            d = math.hypot(x, y)

            if d == 0:
                return __v

            return x + x / d * factor, y + y / d * factor

        x, y = tuple(zip(*map(__transform, zip(*v))))
        return x, y

    @classmethod
    def spiral(cls, resolution: int, k: float = 1.0) -> Vertices:
        k2_pi_p = 2 * k * pi / resolution
        return (
            map(lambda a: sin(a * k2_pi_p) * a / resolution, cls.range(resolution)),
            map(lambda a: cos(a * k2_pi_p) * a / resolution, cls.range(resolution))
        )

    @classmethod
    def circle(cls, angle_deg: int, resolution: int) -> Vertices:
        k2_pi_p = 2 * angle_deg * pi / (resolution * 360)
        return (
            map(lambda a: sin(a * k2_pi_p), cls.range(resolution)),
            map(lambda a: cos(a * k2_pi_p), cls.range(resolution))
        )

    @staticmethod
    def lineSimple() -> Vertices:
        return (0, 1), (0, 1)

    @classmethod
    def nGon(cls, vertex_count: int, resolution: int) -> Vertices:
        angle = 360 // vertex_count
        angles = tuple(map(radians, range(0, 360, angle)))
        return cls.polygon((map(sin, angles), map(cos, angles)), resolution)

    @classmethod
    def rect(cls, resolution: int) -> Vertices:
        return cls.polygon(((1, -1, -1, 1), (1, 1, -1, -1)), resolution)

    @classmethod
    def polygon(cls, vertices: Vertices, resolution: int) -> Vertices:
        x, y = zip(*(map(lambda _: cls.line(*_), (
            (*pos, resolution)
            for pos in pairwise(cls.appendFirst(zip(*vertices)))
        ))))
        return chain(*x), chain(*y)

    @classmethod
    def line[T: Number](cls, begin: Vec2D[T], end: Vec2D[T], resolution: int) -> Vertices:
        x0, y0 = begin
        x1, y1 = end
        return (
            map(lambda t: cls.mix(x0, x1, t), cls.rangeNorm(resolution)),
            map(lambda t: cls.mix(y0, y1, t), cls.rangeNorm(resolution))
        )

    @classmethod
    def rangeNorm(cls, resolution: int) -> Iterable[float]:
        return map(lambda n: n / resolution, cls.range(resolution))

    @staticmethod
    def range(resolution: int) -> Iterable[int]:
        return range(resolution + 1)

    @staticmethod
    def appendFirst[T](i: Iterable[T]) -> Iterable[T]:
        i = iter(i)
        first = next(i, None)

        if first is not None:
            yield first

        yield from i
        yield first

    @staticmethod
    def mix[T: Number](__from: T, __end: T, t: float) -> T:
        return __end * t + (1.0 - t) * __from
