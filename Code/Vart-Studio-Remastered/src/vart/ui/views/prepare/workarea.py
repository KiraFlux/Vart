from typing import Final, ClassVar, Mapping, Any

from kf_dpg.abc.entities import Container
from kf_dpg.core.custom import CustomWidget
from kf_dpg.core.dpg.plot import Plot, DragPoint, LineSeries, DragLine
from kf_dpg.etc.dialog import EditDialog
from kf_dpg.impl.boxes import IntInput
from kf_dpg.impl.buttons import Button
from kf_dpg.impl.containers import VBox, HBox
from kf_dpg.misc.color import Color
from kf_dpg.misc.vector import Vector2D
from vart.assets import Assets
from vart.detail.mesh import Mesh, MeshRegistry
from vart.detail.trajectory import Trajectory
from vart.detail.transformation import Transformation
from vart.detail.workarea import WorkArea


class MeshPlotView(CustomWidget):
    _color_invalid_tool_id: ClassVar = Color.discord_danger()
    _color_from_tool_id: ClassVar[Mapping[int, Color]] = {
        0: Color.gray(0.6).with_alpha(0.5),
        1: Color.discord_nitro(),
        2: Color.discord_warning(),
    }

    def __init__(self, mesh: Mesh, plot: Container):
        translation_point: Final = DragPoint(_value=Vector2D(0, 0), _color=Color.gray(0.8))
        plot.add(translation_point)

        super().__init__(
            translation_point
            .with_handler(mesh.transformation.set_translation)
        )

        def update_name(name: str) -> None:
            translation_point.set_label(name)

        def _update_transformation(transformation: Transformation) -> None:
            translation_point.set_value(transformation.translation)

        update_name(mesh.name)
        mesh.on_name_changed.add_listener(update_name)
        self.attach_delete_observer(lambda _: mesh.on_name_changed.remove_listener(update_name))

        _update_transformation(mesh.transformation)
        mesh.transformation.on_change.add_listener(_update_transformation)
        self.attach_delete_observer(
            lambda _: mesh.transformation.on_change.remove_listener(_update_transformation)
        )

        def add_trajectory(trajectory: Trajectory) -> None:
            line_series = LineSeries.make()
            plot.add(line_series)

            def update_loop(loop: bool):
                line_series.set_loop(loop)

            trajectory.on_loop_changed.add_listener(update_loop)
            update_loop(trajectory.loop)

            def update_color(tool_id: int):
                line_series.set_color(self._color_from_tool_id.get(tool_id, self._color_invalid_tool_id))

            trajectory.on_tool_id_changed.add_listener(update_color)
            update_color(trajectory.tool_id)

            def update_trajectory_vertices(_: Any = None):
                line_series.set_value(trajectory.transformed(mesh.transformation.apply))

            trajectory.on_vertices_changed.add_listener(update_trajectory_vertices)
            mesh.transformation.on_change.add_listener(update_trajectory_vertices)
            update_trajectory_vertices()

            def remove(__t: Trajectory):
                if __t is not trajectory:
                    return

                trajectory.on_loop_changed.remove_listener(update_loop)
                trajectory.on_tool_id_changed.remove_listener(update_color)
                trajectory.on_vertices_changed.remove_listener(update_trajectory_vertices)
                mesh.transformation.on_change.remove_listener(update_trajectory_vertices)
                mesh.trajectories.on_remove.remove_listener(remove)

                line_series.delete()

            mesh.trajectories.on_remove.add_listener(remove)

        for t in mesh.trajectories.values():
            add_trajectory(t)

        mesh.trajectories.on_add.add_listener(add_trajectory)
        self.attach_delete_observer(lambda _: mesh.trajectories.on_add.remove_listener(add_trajectory))


class WorkAreaEditDialog(EditDialog):

    @classmethod
    def _get_title(cls, value: WorkArea) -> str:
        return "Редактирование рабочей области"

    def begin(self, work_area: WorkArea) -> None:
        super().begin(work_area)

        self._width.set_value(work_area.width)
        self._width.set_handler(work_area.set_width)

        self._height.set_value(work_area.height)
        self._height.set_handler(work_area.set_height)

    def __init__(self) -> None:
        def _make_input():
            return IntInput(step=10, step_fast=100).with_interval((0, 10000))

        self._width = _make_input()
        self._height = _make_input()

        super().__init__(
            VBox()
            .add(
                self._width
                .with_label("Ширина")
            )
            .add(
                self._height
                .with_label("Высота")
            )
        )


class WorkAreaView(CustomWidget):
    _drag_step: ClassVar = 50
    _drag_color: ClassVar = Color.discord_secondary()

    @classmethod
    def _sanitise_value(cls, value: float) -> float:
        return int(abs(value // cls._drag_step)) * cls._drag_step

    @classmethod
    def _make_drag_line(cls, *, is_vertical: bool):
        return DragLine.make(is_vertical=is_vertical).with_color(cls._drag_color)

    def __init__(self, mesh_registry: MeshRegistry, work_area: WorkArea):
        drag_line_left = self._make_drag_line(is_vertical=True)
        drag_line_right = self._make_drag_line(is_vertical=True)

        def on_work_area_width_changed(width: float) -> None:
            _half_width = width / 2
            drag_line_left.set_value(-_half_width)
            drag_line_right.set_value(_half_width)

        work_area.on_width_changed.add_listener(on_work_area_width_changed)
        on_work_area_width_changed(work_area.width)

        drag_line_up = self._make_drag_line(is_vertical=False)
        drag_line_down = self._make_drag_line(is_vertical=False)

        def on_work_area_height_changed(height: float) -> None:
            _half_height = height / 2
            drag_line_up.set_value(_half_height)
            drag_line_down.set_value(-_half_height)

        work_area.on_height_changed.add_listener(on_work_area_height_changed)
        on_work_area_height_changed(work_area.height)

        def on_left_dragged(value: float) -> None:
            abs_value = self._sanitise_value(value)
            drag_line_right.set_value(abs_value)
            work_area.set_width(abs_value * 2)

        def on_right_dragged(value: float) -> None:
            abs_value = self._sanitise_value(value)
            drag_line_left.set_value(-abs_value)
            work_area.set_width(abs_value * 2)

        def on_up_dragged(value: float) -> None:
            abs_value = self._sanitise_value(value)
            drag_line_down.set_value(-abs_value)
            work_area.set_height(abs_value * 2)

        def on_down_dragged(value: float) -> None:
            abs_value = self._sanitise_value(value)
            drag_line_up.set_value(abs_value)
            work_area.set_height(abs_value * 2)

        plot: Final = Plot()
        self._edit_dialog: Final = WorkAreaEditDialog().with_font(Assets.default_font)

        super().__init__(
            VBox()
            .add(
                HBox()
                .add(
                    Button()
                    .with_width(200)
                    .with_label("Импорт")
                )
                .add(
                    Button()
                    .with_width(200)
                    .with_label("Экспорт")
                )
                .add(
                    Button()
                    .with_width(-1)
                    .with_label("Рабочая область")
                    .with_handler(lambda: self._edit_dialog.begin(work_area))
                )
            )
            .add(
                plot
                .with_width(-1)
                .with_height(-1)
                .add(
                    drag_line_right
                    .with_handler(on_left_dragged)
                )
                .add(
                    drag_line_left
                    .with_handler(on_right_dragged)
                )
                .add(
                    drag_line_up
                    .with_handler(on_up_dragged)
                )
                .add(
                    drag_line_down
                    .with_handler(on_down_dragged)
                )
            )
        )

        self.attach_delete_observer(lambda _: work_area.on_width_changed.remove_listener(on_work_area_width_changed))
        self.attach_delete_observer(lambda _: work_area.on_height_changed.remove_listener(on_work_area_height_changed))

        def add_mesh_plot_item(_mesh: Mesh) -> None:
            view = MeshPlotView(_mesh, plot)  # Размещает себя

            def remove(__m: Mesh):
                if __m is _mesh:
                    view.delete()

            mesh_registry.on_remove.add_listener(remove)

        for mesh in mesh_registry.values():
            add_mesh_plot_item(mesh)

        mesh_registry.on_add.add_listener(add_mesh_plot_item)
