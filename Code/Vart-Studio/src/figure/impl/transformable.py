"""Трансформируемая фигура"""

from __future__ import annotations

import math
from abc import abstractmethod
from typing import Callable
from typing import ClassVar
from typing import Iterable
from typing import Optional

from figure.abc import Canvas
from figure.abc import Figure
from gen.trajectory import Trajectory
from gen.vertex import Vec2f
from gen.vertex import Vec2i
from gen.vertex import VertexGenerator
from gen.vertex import Vertices
from ui.color import Color
from ui.widgets.abc import ItemID
from ui.widgets.custom.input2d import InputInt2D
from ui.widgets.dpg.impl import Button
from ui.widgets.dpg.impl import Checkbox
from ui.widgets.dpg.impl import CollapsingHeader
from ui.widgets.dpg.impl import DragPoint
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.impl import Separator
from ui.widgets.dpg.impl import SliderInt
from ui.widgets.dpg.theme import LineSeriesTheme


class TransformableFigure[T: "TransformableFigure"](Figure):
    INPUT_WIDTH: ClassVar[int] = 200
    DEFAULT_SIZE: ClassVar[Vec2i] = (100, 100)

    COLORS: ClassVar[int, Color] = {
        0: Color(0xFF, 0, 0, 0x80),
        1: Color(0xFF, 0x80, 0x20),
        2: Color(0x20, 0xFF, 0x80),
        3: Color(0x20, 0x80, 0xFF),
    }

    COLOR_NOT_PRINT = Color(0x80, 0x80, 0x80, 0x80)

    def __init__(
            self,
            vertices: Vertices,
            label: str,
            on_delete: Callable[[TransformableFigure], None],
            on_clone: Callable[[TransformableFigure], None]
    ) -> None:
        super().__init__(vertices, label, self.DEFAULT_SIZE)

        self._name = label
        self._on_delete = on_delete
        self._on_clone = on_clone

        self._planner_mode_input = InputInt("Режим планировщика", value_range=(0, 2), default_value=2)

        self._tool_id_input = InputInt("Инструмент", self.__updateDisplayColor, value_range=(1, 2), default_value=1, width=self.INPUT_WIDTH)

        self._rotation_input = InputInt("Поворот", self.__onRotationInputChanged, value_range=(-360, 360), default_value=0, step=2, step_fast=5, width=self.INPUT_WIDTH)

        self._inflate_input = SliderInt("Вздутие", lambda _: self.update(), value_range=(-100, 100))

        self._position_point = DragPoint(self.__onPositionPointChanged, label="Position")
        self._size_point = DragPoint(self.__onSizeChanged, label="Размер", default_value=self.getSize())
        self._controls_visibility_checkbox = Checkbox(self.__onSetControlsVisibleChanged, label="Видимость элементов управления", default_value=True)
        self._export_checkbox = Checkbox(self.__updateDisplayColor, label="Для печати", default_value=True)
        self._show_points_checkbox = Checkbox(self.__updateDisplayColor, label="Показать вершины", default_value=False)

        self._input_scale = InputInt2D(
            "Масштаб",
            self.__onUpdateScaleInput,
            default_value=self.getSize(),
            value_range=(1, 10000),
            x_label="Ширина",
            y_label="Высота",
            input_width=self.INPUT_WIDTH,
            step=5,
            step_fast=20,
            reset_button=True
        )

        self._input_position = InputInt2D(
            "Позиция",
            self.__onPositionInputChange,
            input_width=self.INPUT_WIDTH,
            step=10,
            step_fast=50,
            value_range=(-10000, 10000)
        )

        self.__sin_angle: float = 0
        self.__cos_angle: float = 0
        self.__calcRotation(0)

    def _getToolColor(self) -> Color:
        return self.COLORS.get(self._tool_id_input.getValue(), 0)

    def _getDisplayColor(self) -> Color:
        if self._export_checkbox.getValue():
            return self._getToolColor()
        return self.COLOR_NOT_PRINT

    def __updateDisplayColor(self, _=None) -> None:
        self._setColor(self._getDisplayColor(), self._show_points_checkbox.getValue())

    def _setColor(self, color: Color, has_points: bool) -> None:
        self.setTheme(LineSeriesTheme.getInstance().get(color, has_dots=has_points))

    def __calcRotation(self, angle_degrees: float) -> None:
        angle_radians = math.radians(angle_degrees)
        self.__sin_angle = math.sin(angle_radians)
        self.__cos_angle = math.cos(angle_radians)

    def getPosition(self) -> Vec2f:
        """Получить текущую позицию"""
        return self._position_point.getValue()

    def setPosition(self, position: Vec2f) -> None:
        """Получить позицию фигуры"""
        self._position_point.setValue(position)
        self.__updateSizePoint(*position)

    def setSize(self, size: Vec2i) -> None:
        super().setSize(size)
        size_x, size_y = size
        position_x, position_y = self.getPosition()
        self._size_point.setValue((position_x + size_x, position_y + size_y))

    def toTrajectory(self) -> Optional[Trajectory]:
        """Конвертировать фигуру в траекторию"""

        if not self._export_checkbox.getValue():
            return

        x, y = self.getTransformedVertices()
        return Trajectory(
            name=self._name,
            x_positions=x,
            y_positions=y,
            tool=self._tool_id_input.getValue(),
            planner_mode=self._planner_mode_input.getValue()
        )

    def _getTransformedVertices(self, in_v: tuple[Iterable[float], Iterable[float]]):
        transformed_x = list[int]()
        transformed_y = list[int]()

        size_x, size_y = self.getSize()
        position_x, position_y = self.getPosition()

        sin_angle = self.__sin_angle
        cos_angle = self.__cos_angle

        for x, y in zip(*in_v):
            x *= size_x
            y *= size_y

            new_x = int(cos_angle * x - sin_angle * y + position_x)
            new_y = int(sin_angle * x + cos_angle * y + position_y)

            if len(transformed_x) > 0 and (new_x == transformed_x[-1]) and (new_y == transformed_y[-1]):
                continue

            transformed_x.append(new_x)
            transformed_y.append(new_y)

        return transformed_x, transformed_y

    def getTransformedVertices(self) -> tuple[Iterable[int], Iterable[int]]:
        v = self._source_vertices_x, self._source_vertices_y

        inflate = self.getInflate()
        if inflate != 0:
            v = VertexGenerator.inflate(v, inflate)

        return self._getTransformedVertices(v)

    def getInflate(self) -> float:
        return self._inflate_input.getValue()

    def setInflate(self, factor: float) -> None:
        return self._inflate_input.setValue(factor)

    def attachIntoCanvas(self, canvas: Canvas) -> None:
        canvas.axis.add(self)
        canvas.add(self._position_point)
        canvas.add(self._size_point)
        self.update()

    def delete(self) -> None:
        super().delete()
        self._on_delete(self)
        self._position_point.delete()
        self._size_point.delete()

    @abstractmethod
    def _getCloneInstance(
            self,
            name: str,
            on_delete: Callable[[T], None],
            on_clone: Callable[[T], None]
    ) -> T:
        """Получить реализацию клона"""

    def clone(self) -> TransformableFigure:
        """Создать клон фигуры"""
        return self._getCloneInstance(f"Копия {self._name}", self._on_delete, self._on_clone)

    def transformClone(self, clone: TransformableFigure) -> TransformableFigure:
        """Сделать преобразования над клоном фигуры"""
        self.setVertices(self.getTransformedVertices())
        clone.setRotation(self.getRotation())
        clone.setSize(self._input_scale.getValue())
        clone.update()
        return clone

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self._controls_visibility_checkbox)
        self.add(Button("Удалить", self.delete))
        self.add(Button("Дублировать", lambda: self._on_clone(self)))

        (
            CollapsingHeader("Параметры Печати", default_open=True).place(self)
            .add(self._export_checkbox)
            .add(self._tool_id_input)
            .add(self._planner_mode_input)
            .add(Separator())
        )

        (
            CollapsingHeader("Трансформация", default_open=True).place(self)
            .add(self._input_scale)
            .add(self._rotation_input)
            .add(Button("Сбросить", lambda: self.setRotation(0)))
            .add(Separator())
            .add(self._input_position)
        )

        self.add(self._show_points_checkbox)
        self.add(Separator())

        (
            CollapsingHeader("Эффекты", default_open=False).place(self)
            .add(self._inflate_input)
        )

        self.add(Separator())
        self.__updateDisplayColor()

    def __onPositionInputChange(self, new_position: Vec2i) -> None:
        self.setPosition(new_position)
        self.update()

    def __onUpdateScaleInput(self, new_scale: Vec2i) -> None:
        self.setSize(new_scale)
        self.update()

    def __onPositionPointChanged(self, new_position: Vec2f) -> None:
        self.__updateSizePoint(*new_position)
        # noinspection PyTypeChecker
        self._input_position.setValue(new_position)
        self.update()

    def __updateSizePoint(self, position_x: float, position_y: float) -> None:
        scale_x, scale_y = self.getSize()
        self._size_point.setValue(((position_x + scale_x), (position_y + scale_y)))

    def __onSizeChanged(self, new_scale: Vec2f) -> None:
        scale_x, scale_y = new_scale
        position_x, position_y = self.getPosition()
        size = int(scale_x - position_x), int(scale_y - position_y)

        self.setSize(size)
        self._input_scale.setValue(size)
        self.update()

    def __onRotationInputChanged(self, new_angle: int) -> None:
        self.__calcRotation(new_angle)
        self.update()

    def setRotation(self, angle_degrees: int) -> None:
        """Установить поворот"""
        self._rotation_input.setValue(angle_degrees)
        self.__calcRotation(angle_degrees)
        self.update()

    def __onSetControlsVisibleChanged(self, is_visible: bool) -> None:
        self._position_point.setVisible(is_visible)
        self._size_point.setVisible(is_visible)

    def _cloneVertices(self) -> tuple[Iterable[float], Iterable[float]]:
        return (
            self._source_vertices_x,
            self._source_vertices_y
        )

    def getRotation(self) -> int:
        """Получить угол поворота фигуры"""
        return self._rotation_input.getValue()
