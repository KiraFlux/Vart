"""Приложение для маркерного плоттера"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from application.widgets.settings import CodeGeneratorSettngsWidget
from bytelang.compiler import ByteLangCompiler
from bytelang.utils import LogFlag
from dearpygui import dearpygui as dpg
from figure.abc import Canvas
from figure.impl.workarea import WorkAreaFigure
from figure.registry import FigureRegistry
from gen.enums import PlannerMode
from gen.movementprofile import MovementProfile
from gen.settings import GeneratorSettings
from gen.writer import CodeWriter
from loader.mesh import LegacyMeshFigure
from ui.application import Application
from ui.widgets.custom.logger import LoggerWidget
from ui.widgets.dpg.impl import Button
from ui.widgets.dpg.impl import FileDialog
from ui.widgets.dpg.impl import Menu


class VARTApplication(Application):
    """Приложение"""

    def __init__(self, resources_path: Path) -> None:
        self._logger = LoggerWidget()
        self._log_flags = LogFlag.PROGRAM_SIZE | LogFlag.COMPILATION_TIME | LogFlag.BYTECODE

        self._res_path = resources_path

        self._image_file_dialog = FileDialog(
            "Укажите файл obj для вставки", self.onObjFileSelected,
            (("obj", "Object"),),
            resources_path / "res/obj"
        )

        self._export_file_dialog = FileDialog(
            "Укажите файл для экспорта", lambda paths: self._onWriteBytecode(paths[0]),
            extensions=(("blc", "VART ByteCode"),),
            default_path=(resources_path / "res/out")
        )

        self._work_area = WorkAreaFigure("Рабочая область")

        self._figure_registry = FigureRegistry(Canvas())

        self._generator_settings = GeneratorSettings(
            MovementProfile(name="Перемещение", mode=PlannerMode.ACCEL, speed=200, accel=75),
            MovementProfile(name="Продолжительный отрезок", mode=PlannerMode.ACCEL, speed=150, accel=50),
            MovementProfile(name="Кривая (Короткий отрезок)", mode=PlannerMode.SPEED, speed=20, accel=0),
            MovementProfile(name="Малые отрезки", mode=PlannerMode.POSITION, speed=0, accel=0),
            tool_change_begin_timeout_ms=1000,
            tool_change_end_timeout_ms=1000,
            epilogue_stop_duration_ms=1000,
            epilogue_end_position=(0, 0)
        )

        self._bytecode_writer = CodeWriter(self._generator_settings, ByteLangCompiler.simpleSetup(resources_path / "res/bytelang"))

    def onObjFileSelected(self, paths: Sequence[Path]) -> None:
        """
        Callback при открытии файла
        :param paths:
        """
        # print(paths)

        for path in paths:
            obj_figures = LegacyMeshFigure.load(path, self._figure_registry.onFigureDelete, self._figure_registry.onFigureClone)

            for obj in obj_figures:
                self._figure_registry.add(obj)

    def _printTrajectories(self) -> None:
        self._logger.write("\n".join(map(str, self._figure_registry.getTrajectories())))

    def _onWriteBytecode(self, output_path: Path) -> None:
        with open(output_path, "wb") as bytecode_stream:
            trajectories = self._figure_registry.getTrajectories()

            result = self._bytecode_writer.run(trajectories, bytecode_stream)

            self._logger.write(result.getMessage())

    def build(self) -> None:
        self._image_file_dialog.build()
        self._export_file_dialog.build()

        self._buildMenuBar()
        self._buildTabBar()
        self._buildWidgets()

        self._makeTheme()
        self._makeFont()

    def _buildWidgets(self):
        self._figure_registry.canvas.addFigure(self._work_area)
        self._figure_registry.addPolygon()
        self._work_area.setDeadZone(50, 50, 20, 120, -80)
        self._work_area.setSize((500, 700))

    def _buildTabBar(self):
        with dpg.tab_bar():
            with dpg.tab(label="Область печати"):
                self._figure_registry.canvas.place()

            with dpg.tab(label="Настройки"):
                CodeGeneratorSettngsWidget(self._generator_settings).place()

            with dpg.tab(label="Журнал"):
                self._logger.place()

    def _buildMenuBar(self):
        with dpg.menu_bar():
            (
                Menu("Файл").place()
                .add(Button("Открыть", self._image_file_dialog.show))
                .add(Button("Экспорт", self._export_file_dialog.show))
            )

            dpg.add_separator()

            Button("Очистить", self._figure_registry.clear).place()

            (
                Menu("Вставка").place()
                .add(Button("Полигон", self._figure_registry.addPolygon))
                .add(Button("Прямоугольник", self._figure_registry.addRect))
                .add(Button("Круг", self._figure_registry.addCircle))
                .add(Button("Спираль", self._figure_registry.addSpiral))
                .add(Button("Линия", self._figure_registry.addLine))
            )

            dpg.add_separator()

            (
                Menu("Dev").place()
                .add(Button("Вывод траекторий", self._printTrajectories))
                .add(Button("show_implot_demo", dpg.show_implot_demo))
                .add(Button("show_font_manager", dpg.show_font_manager))
                .add(Button("show_style_editor", dpg.show_style_editor))
                .add(Button("show_imgui_demo", dpg.show_imgui_demo))
                .add(Button("show_item_registry", dpg.show_item_registry))
                .add(Button("show_metrics", dpg.show_metrics))
                .add(Button("show_debug", dpg.show_debug))
            )

    def _makeFont(self):
        with dpg.font_registry():
            p = self._res_path / r"res/fonts/Roboto-Mono/RobotoMono.ttf"
            print(p)
            with dpg.font(p, 20, default_font=True) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.bind_font(font)

    @staticmethod
    def _makeTheme():
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
        dpg.bind_theme(global_theme)
