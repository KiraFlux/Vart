from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dearpygui import dearpygui as dpg

from gen.vertex import Vec2i
from gen.vertex import Vertices
from ui.widgets.abc import ItemID
from ui.widgets.dpg.impl import Axis
from ui.widgets.dpg.impl import LineSeries
from ui.widgets.dpg.impl import Plot


class Figure(LineSeries, ABC):
    """Фигура, изображенная на холсте"""

    def __init__(self, vertices: Vertices, label: str, size: Vec2i = (0, 0)) -> None:
        super().__init__(label)
        x, y = vertices
        self._source_vertices_x = tuple(x)
        self._source_vertices_y = tuple(y)
        self.__size = size

    def setVertices(self, new_vertices: Vertices) -> None:
        """Задать значения вершин"""
        x, y = new_vertices
        self._source_vertices_x = tuple(x)
        self._source_vertices_y = tuple(y)

    @abstractmethod
    def getTransformedVertices(self) -> Vertices:
        """Получить трансформированные вершины"""

    @abstractmethod
    def attachIntoCanvas(self, canvas: Canvas) -> None:
        """Добавить на холст эту фигуру"""

    def getSize(self) -> Vec2i:
        """Получить масштаб фигуры"""
        return self.__size

    def setSize(self, size: Vec2i) -> None:
        """Установить масштаб фигуры"""
        self.__size = size

    def update(self) -> None:
        """Обновить показания на холсте"""
        self.setValue(self.getTransformedVertices())


class Canvas(Plot):

    def __init__(self) -> None:
        super().__init__()
        self.axis = Axis(dpg.mvXAxis)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.axis)

    def addFigure(self, figure: Figure) -> None:
        """Добавить фигуру"""
        figure.attachIntoCanvas(self)
