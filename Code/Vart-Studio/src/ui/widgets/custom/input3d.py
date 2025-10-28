from typing import Callable
from typing import Optional

from ui.widgets.abc import ItemID
from ui.widgets.abc import VariableItem
from ui.widgets.dpg.impl import Button
from ui.widgets.dpg.impl import Group
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.impl import Text

type vec3 = tuple[int, int, int]


class InputInt3D(Group, VariableItem[vec3]):

    def __init__(
            self, /,
            title: str,
            on_change: Callable[[vec3], None],
            value_range: tuple[int, int], *,
            step: int = 1,
            step_fast: int = 10,
            reset_button: bool = False,
            default_value: vec3 = (0, 0, 0),
            width: int = 300,
    ) -> None:
        super().__init__()

        self.__title = title
        self.__has_reset_button = reset_button

        dx, dy, dz = default_value

        self._default_value = default_value
        self._on_change: Optional[Callable[[vec3], None]] = on_change

        self._x = InputInt(
            "x",
            lambda x: self.setValue((x, None, None)),
            width=width,
            value_range=value_range,
            default_value=dx,
            step=step,
            step_fast=step_fast,
        )

        self._y = InputInt(
            "y",
            lambda y: self.setValue((None, y, None)),
            width=width,
            value_range=value_range,
            default_value=dy,
            step=step,
            step_fast=step_fast

        )

        self._z = InputInt(
            "z",
            lambda z: self.setValue((None, None, z)),
            width=width,
            value_range=value_range,
            default_value=dz,
            step=step,
            step_fast=step_fast
        )

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)

        (
            self.add(Text(self.__title))
            .add(self._x)
            .add(self._y)
            .add(self._z)
        )

        if self.__has_reset_button:
            self.add(Button("Сброс", lambda: self.setValue(self._default_value)))

        del self.__title
        del self.__has_reset_button

    def setValue(self, value: tuple[Optional[int], Optional[int], Optional[int]]) -> None:
        x, y, z = value

        if x is not None:
            self._x.setValue(x)
        else:
            x = self.getX()

        if y is not None:
            self._y.setValue(y)
        else:
            y = self.getY()

        if z is not None:
            self._z.setValue(z)
        else:
            z = self.getZ()

        if self._on_change is not None:
            self._on_change((x, y, z))

    def getValue(self) -> vec3:
        return self.getX(), self.getY(), self.getZ()

    def getX(self) -> int:
        return self._x.getValue()

    def getY(self) -> int:
        return self._y.getValue()

    def getZ(self) -> int:
        return self._z.getValue()
