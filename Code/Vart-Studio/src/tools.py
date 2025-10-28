from dataclasses import dataclass
from typing import Callable
from typing import Sequence


@dataclass
class Range[T]:
    """Диапазон значений"""

    min: T
    """Минимальное из этого диапазона"""
    max: T
    """Максимальное"""

    def asTuple(self) -> tuple[T, T]:
        """Представить в виде кортежа"""
        return self.min, self.max

    def clamp(self, value: T) -> T:
        """Получить значение ограниченное диапазоном"""
        return min(self.max, max(self.min, value))


def greedySort[T, F](original: Sequence[T], metric: Callable[[T, T], F]) -> list[T]:
    n = len(original)
    ret = [original[0]]

    used = {0}
    uses = 1

    while uses < n:
        last = ret[-1]

        nearest_index = min(
            filter(lambda i: i not in used, range(n)),
            key=lambda i: metric(last, original[i]),
            default=None
        )

        if nearest_index is not None:
            ret.append(original[nearest_index])
            used.add(nearest_index)
            uses += 1

    return ret
