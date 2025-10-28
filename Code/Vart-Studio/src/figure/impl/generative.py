from __future__ import annotations

from abc import abstractmethod
from typing import Callable

from figure.impl.transformable import TransformableFigure
from gen.vertex import VertexGenerator
from gen.vertex import Vertices
from ui.widgets.abc import ItemID
from ui.widgets.dpg.impl import CollapsingHeader
from ui.widgets.dpg.impl import InputInt


class GenerativeFigure[T: "GenerativeFigure"](TransformableFigure[T]):

    def __init__(self, label: str, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> None:
        super().__init__((tuple(), tuple()), label, on_delete, on_clone)

        self._resolution_input = InputInt(
            "Разрешение",
            value_range=VertexGenerator.RESOLUTION_RANGE.asTuple(),
            default_value=1,
            on_change=lambda _: self.update(),
        )

        self._header = CollapsingHeader("Прочее", default_open=True)

    def transformClone(self, clone: GenerativeFigure) -> TransformableFigure:
        clone.setResolution(self.getResolution())
        return super().transformClone(clone)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self._header.place(self).add(self._resolution_input)

    def getResolution(self) -> int:
        """Получить разрешение"""
        return self._resolution_input.getValue()

    def setResolution(self, new_resolution: int) -> None:
        """Установить разрешение"""
        self._resolution_input.setValue(new_resolution)

    @abstractmethod
    def _generateVertices(self) -> Vertices:
        """Сгенерировать фигуру"""

    def getTransformedVertices(self) -> Vertices:
        self.setVertices(self._generateVertices())
        return super().getTransformedVertices()


class RectFigure(GenerativeFigure["RectFigure"]):

    def _getCloneInstance(self, name: str, on_delete: Callable[[RectFigure], None], on_clone: Callable[[RectFigure], None]) -> RectFigure:
        return RectFigure(name, on_delete, on_clone)

    def _generateVertices(self) -> Vertices:
        return VertexGenerator.rect(self.getResolution())


class CircleFigure(GenerativeFigure):

    def __init__(self, label: str, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> None:
        super().__init__(label, on_delete, on_clone)
        self._angle_input = InputInt(
            "Угол",
            on_change=lambda _: self.update(),
            width=TransformableFigure.INPUT_WIDTH,
            default_value=360,
            step=5,
            step_fast=15,
            value_range=(1, 360)
        )

    def getAngle(self) -> int:
        return self._angle_input.getValue()

    def setAngle(self, angle: int) -> None:
        return self._angle_input.setValue(angle)

    def _getCloneInstance(self, name: str, on_delete: Callable[[CircleFigure], None], on_clone: Callable[[CircleFigure], None]) -> CircleFigure:
        return CircleFigure(name, on_delete, on_clone)

    def _generateVertices(self) -> Vertices:
        return VertexGenerator.circle(self.getAngle(), self.getResolution())

    def transformClone(self, clone: CircleFigure) -> TransformableFigure:
        clone.setAngle(self.getAngle())
        return super().transformClone(clone)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self._header.add(self._angle_input)


class SpiralFigure(GenerativeFigure):

    def _getCloneInstance(self, name: str, on_delete: Callable[[SpiralFigure], None], on_clone: Callable[[SpiralFigure], None]) -> SpiralFigure:
        return SpiralFigure(name, on_delete, on_clone)

    def __init__(self, label: str, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> None:
        super().__init__(label, on_delete, on_clone)
        self._repeats_count = InputInt("Витки", on_change=lambda _: self.update(), width=TransformableFigure.INPUT_WIDTH, default_value=1, value_range=VertexGenerator.SPIRAL_REPEATS.asTuple())

    def transformClone(self, clone: SpiralFigure) -> TransformableFigure:
        clone.setRepeatsCount(self.getRepeatsCount())
        return super().transformClone(clone)

    def setRepeatsCount(self, repeats: int) -> None:
        """Установить количество витков"""
        self._repeats_count.setValue(repeats)

    def getRepeatsCount(self) -> int:
        """Получить количество витков"""
        return self._repeats_count.getValue()

    def _generateVertices(self) -> Vertices:
        return VertexGenerator.spiral(self.getResolution(), self._repeats_count.getValue())

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self._header.add(self._repeats_count)


class PolygonFigure(GenerativeFigure):

    def _getCloneInstance(self, name: str, on_delete: Callable[[GenerativeFigure], None], on_clone: Callable[[GenerativeFigure], None]) -> GenerativeFigure:
        return PolygonFigure(name, on_delete, on_clone)

    def __init__(self, label: str, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> None:
        super().__init__(label, on_delete, on_clone)
        self._vertex_count = InputInt("Вершины", on_change=lambda _: self.update(), width=TransformableFigure.INPUT_WIDTH, default_value=6,
                                      value_range=VertexGenerator.POLYGON_VERTEX_COUNT_RANGE.asTuple())

    def transformClone(self, clone: PolygonFigure) -> TransformableFigure:
        clone.setVertexCount(self.getVertexCount())
        return super().transformClone(clone)

    def _generateVertices(self) -> Vertices:
        return VertexGenerator.nGon(self.getVertexCount(), self.getResolution())

    def getVertexCount(self) -> int:
        """Получить количество вершин полигона"""
        return self._vertex_count.getValue()

    def setVertexCount(self, count: int) -> None:
        """Установить количество вершин полигона"""
        self._vertex_count.setValue(count)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self._header.add(self._vertex_count)


class LineFigure(GenerativeFigure):

    def _getCloneInstance(self, name: str, on_delete: Callable[[TransformableFigure], None], on_clone: Callable[[TransformableFigure], None]) -> TransformableFigure:
        return LineFigure(name, on_delete, on_clone)

    def _generateVertices(self) -> Vertices:
        return VertexGenerator.lineSimple()
