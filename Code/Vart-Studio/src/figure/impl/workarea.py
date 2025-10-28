from __future__ import annotations

from typing import Final

from figure.abc import Canvas
from figure.abc import Figure
from gen.vertex import Vec2i
from gen.vertex import Vertices
from ui.color import Color
from ui.color import WORK_AREA
from ui.widgets.abc import ItemID
from ui.widgets.custom.border import Border
from ui.widgets.dpg.impl import CollapsingHeader
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.theme import LineSeriesTheme


class WorkAreaFigure(Figure):
    __WORK_AREA_VERTICES: Final[Vertices] = (
        (0.5, 0.5, -0.5, -0.5, 0.5),
        (0.5, -0.5, -0.5, 0.5, 0.5)
    )

    WORK_AREA_COLOR: Final[Color] = WORK_AREA

    def __init__(self, label: str):
        super().__init__(self.__WORK_AREA_VERTICES, label)
        self.__border = Border(self.__onSizeChanged, step=25)

        self.__left_dead_zone_input = InputInt("Лево", self.__onDeadZoneChanged, step=50)
        self.__right_dead_zone_input = InputInt("Право", self.__onDeadZoneChanged, step=50)
        self.__bottom_dead_zone_input = InputInt("Низ", self.__onDeadZoneChanged, step=50)
        self.__top_dead_zone_input = InputInt("Верх", self.__onDeadZoneChanged, step=50)
        self.__vertical_offset_input = InputInt("Вертикальный сдвиг", self.__onDeadZoneChanged, step=10, value_range=(-200, 200))

    def getBottomDeadZone(self) -> int:
        """Получить нижнюю границу"""
        return self.__bottom_dead_zone_input.getValue()

    def getTopDeadZone(self) -> int:
        """Получить верхнюю границу"""
        return self.__top_dead_zone_input.getValue()

    def getLeftDeadZone(self) -> int:
        """Получить левую границу"""
        return self.__left_dead_zone_input.getValue()

    def getRightDeadZone(self) -> int:
        """Получить правую границу"""
        return self.__right_dead_zone_input.getValue()

    def getVerticalOffset(self) -> int:
        """Получить вертикальное смещение"""
        return self.__vertical_offset_input.getValue()

    def setDeadZone(self, left: int, right: int, top: int, bottom: int, vertical_offset: int) -> None:
        """Установить смещение"""
        self.__left_dead_zone_input.setValue(left)
        self.__right_dead_zone_input.setValue(right)
        self.__top_dead_zone_input.setValue(top)
        self.__bottom_dead_zone_input.setValue(bottom)
        self.__vertical_offset_input.setValue(vertical_offset)

    def setSize(self, size: Vec2i) -> None:
        super().setSize(size)
        self.__border.setValue(size)

    def attachIntoCanvas(self, canvas: Canvas) -> None:
        canvas.axis.add(self)
        canvas.add(self.__border)

    def getTransformedVertices(self) -> Vertices:
        size_x, size_y = self.getSize()

        left_dead_zone = self.getLeftDeadZone()
        right_dead_zone = self.getRightDeadZone()
        top_dead_zone = self.getTopDeadZone()
        bottom_dead_zone = self.getBottomDeadZone()

        area_width = size_x - left_dead_zone - right_dead_zone
        area_height = size_y - top_dead_zone - bottom_dead_zone

        offset_x = (left_dead_zone - right_dead_zone) / 2
        offset_y = (bottom_dead_zone - top_dead_zone) / 2 + self.getVerticalOffset()

        return (
            [x * area_width + offset_x for x in self._source_vertices_x],
            [y * area_height + offset_y for y in self._source_vertices_y],
        )

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)

        (
            CollapsingHeader("Настройки мёртвой зоны", default_open=True).place(self)
            .add(self.__left_dead_zone_input)
            .add(self.__right_dead_zone_input)
            .add(self.__top_dead_zone_input)
            .add(self.__bottom_dead_zone_input)
            .add(self.__vertical_offset_input)
        )

        self.setTheme(LineSeriesTheme.getInstance().get(self.WORK_AREA_COLOR))

    def __onSizeChanged(self, new_size: Vec2i) -> None:
        super().setSize(new_size)
        new_width, new_height = new_size
        half_width = int(new_width // 2)
        half_height = int(new_height // 2)

        self.__left_dead_zone_input.setMaxValue(half_width)
        self.__right_dead_zone_input.setMaxValue(half_width)
        self.__top_dead_zone_input.setMaxValue(half_height)
        self.__bottom_dead_zone_input.setMaxValue(half_height)

        self.update()

    def __onDeadZoneChanged(self, _) -> None:
        self.update()
