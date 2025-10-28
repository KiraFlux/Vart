from dataclasses import dataclass
from typing import ClassVar

from gen.enums import PlannerMode
from tools import Range


@dataclass(kw_only=True)
class MovementProfile:
    """ПредНастройка перемещения"""

    MODE_RANGE: ClassVar[Range[PlannerMode]] = Range(PlannerMode.POSITION, PlannerMode.ACCEL)
    SPEED_RANGE: ClassVar[Range[int]] = Range(10, 255)
    ACCEL_RANGE: ClassVar[Range[int]] = Range(10, 255)

    name: str
    """Наименование пресета для отладки"""

    mode: PlannerMode
    """Режим планировщика"""

    speed: int
    """Заданная скорость"""

    accel: int
    """Заданное ускорение"""
