from __future__ import annotations

from math import hypot
from typing import Iterable
from typing import Sequence

from figure.abc import Canvas
from figure.impl.generative import CircleFigure
from figure.impl.generative import LineFigure
from figure.impl.generative import PolygonFigure
from figure.impl.generative import RectFigure
from figure.impl.generative import SpiralFigure
from figure.impl.transformable import TransformableFigure
from gen.trajectory import Trajectory
from tools import greedySort


class FigureRegistry:
    """Реестр фигур, расположенных на холсте"""

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self._figures = dict[int, TransformableFigure]()

    def add(self, figure: TransformableFigure) -> None:
        """Добавить фигуру на холст"""
        self._figures[figure.__hash__()] = figure
        self.canvas.addFigure(figure)

    def onFigureDelete(self, figure: TransformableFigure) -> None:
        self._figures.pop(figure.__hash__())

    def onFigureClone(self, figure: TransformableFigure) -> None:
        source_figure = self._figures.get(figure.__hash__())
        clone_figure = source_figure.clone()
        self.add(clone_figure)
        source_figure.transformClone(clone_figure)

    def _makeName(self, source: str) -> str:
        return f"{source.capitalize()}: {self._getCurrentFigureIndex()}"

    def _getCurrentFigureIndex(self) -> int:
        return len(self._figures)

    def addPolygon(self) -> None:
        """Добавить полигон"""
        self.add(PolygonFigure(self._makeName("Полигон"), self.onFigureDelete, self.onFigureClone))

    def addRect(self) -> None:
        """Добавить демо-прямоугольник"""
        self.add(RectFigure(self._makeName("Прямоугольник"), self.onFigureDelete, self.onFigureClone))

    def addSpiral(self) -> None:
        """Добавить спираль"""
        self.add(SpiralFigure(self._makeName("Спираль"), self.onFigureDelete, self.onFigureClone))

    def addCircle(self) -> None:
        """Добавить круг"""
        self.add(CircleFigure(self._makeName("Круг"), self.onFigureDelete, self.onFigureClone))

    def addLine(self) -> None:
        """Добавить линию"""
        self.add(LineFigure(self._makeName("Линия"), self.onFigureDelete, self.onFigureClone))

    def clear(self) -> None:
        """Удалить все фигуры"""
        for figure in self.getFigures():
            figure.delete()

    def getFigures(self) -> Sequence[TransformableFigure]:
        """Получить все фигуры"""
        return list(self._figures.values())

    def getTrajectories(self) -> Iterable[Trajectory]:
        """Получить все траектории"""
        def _k(t1: Trajectory, t2: Trajectory) -> float:
            x1, y1 = t1.centroid()
            x2, y2 = t2.centroid()
            return hypot(x1 - x2, y1 - y2)

        return greedySort(list(filter(None.__ne__, (figure.toTrajectory() for figure in self.getFigures()))), _k)
