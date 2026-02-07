from typing import Final

from kf_dpg.abc.entities import Container
from kf_dpg.core.custom import CustomWidget
from kf_dpg.core.dpg.plot import Plot, DragPoint, LineSeries
from kf_dpg.etc.dialog import EditDialog, ConfirmDialog
from kf_dpg.etc.input2d import FloatInput2D
from kf_dpg.impl.boxes import TextInput, IntInput
from kf_dpg.impl.buttons import Button
from kf_dpg.impl.containers import VBox, ChildWindow, HBox
from kf_dpg.impl.text import Text
from kf_dpg.misc.color import Color
from kf_dpg.misc.vector import Vector2D
from vart.assets import Assets
from vart.detail.mesh import Mesh2D, MeshRegistry
from vart.detail.trajectory import Trajectory
from vart.detail.transformation import Transformation2D
from vart.misc.log import Logger


class MeshEditDialog(EditDialog):

    @classmethod
    def _get_title(cls, mesh: Mesh2D) -> str:
        return f"Edit: '{mesh.name}'"

    def __init__(self):
        self._name: Final = TextInput().with_label("Наименование")
        self._rotation: Final = IntInput(step_fast=15, step=5).with_interval((-360, 360))
        self._scale: Final = FloatInput2D("Масштаб", interval=(-10000, 10000), )
        self._translation: Final = FloatInput2D("Позиция", interval=(-10000, 10000), )

        super().__init__(
            VBox()
            .with_width(160)
            .add(self._name)
            .add(self._rotation)
            .add(self._scale)
            .add(self._translation)
        )

    def begin(self, mesh: Mesh2D) -> None:
        super().begin(mesh)

        self._name.set_value(mesh.name)
        self._name.set_handler(mesh.set_name)

        self._rotation.set_value(mesh.transformation.get_rotation_degrees())
        self._rotation.set_handler(mesh.transformation.set_rotation_degrees)

        self._scale.set_value(mesh.transformation.scale)
        self._scale.set_handler(mesh.transformation.set_scale)

        self._translation.set_value(mesh.transformation.translation)
        self._translation.set_handler(mesh.transformation.set_translation)


class MeshCard(CustomWidget):

    def __init__(
            self, mesh: Mesh2D,
            mesh_registry: MeshRegistry,
            *,
            edit_dialog_button: Button,
            mesh_delete_button: Button,
    ):
        self._target_mesh: Final = mesh

        self._name: Final = Text(color=Color.discord_success())
        self._target_mesh.on_name_changed.add_listener(self._name.set_value)

        mesh_registry.on_remove.add_listener(self.terminate)

        super().__init__(
            ChildWindow()
            .with_height(80)
            .add(
                VBox()
                .add(self._name)
                .add(
                    HBox()
                    .add(
                        mesh_delete_button
                        .with_label(" x ")
                    )
                    .add(
                        Button()
                        .with_handler(lambda: mesh_registry.add_clone(mesh))
                        .with_label("Клонировать")
                    )
                    .add(
                        edit_dialog_button
                        .with_label("···")
                    )
                )
            )
        )

        self._name.set_value(mesh.name)

    def terminate(self, mesh: Mesh2D) -> None:
        if mesh is self._target_mesh:
            self.delete()

    def delete(self) -> None:
        self._target_mesh.on_name_changed.remove_listener(self._name.set_value)
        super().delete()


class MeshList(CustomWidget):

    def __init__(self, mesh_registry: MeshRegistry):
        self._mesh_registry: Final = mesh_registry

        self._mesh_edit_dialog: Final = MeshEditDialog().with_font(Assets.default_font)
        self._dialog: Final = ConfirmDialog().with_font(Assets.default_font)

        self._mesh_list: Final = ChildWindow(
            scrollable_y=True,
        )

        super().__init__(
            VBox()
            .with_width(400)
            .add(
                Button()
                .with_label("Добавить")
                .with_width(-1)
                .with_handler(self._mesh_registry.add_dummy)
            )
            .add(
                Button()
                .with_label("Очистить")
                .with_width(-1)
                .with_handler(
                    lambda: self._dialog.begin(
                        f"Удалить {len(self._mesh_registry.values())} эл.?",
                        on_confirm=self._mesh_registry.clear
                    )
                )
            )
            .add(self._mesh_list)
        )

        for mesh in self._mesh_registry.values():
            self._add_mesh_card(mesh)

        self._mesh_registry.on_add.add_listener(self._add_mesh_card)

    def _add_mesh_card(self, mesh: Mesh2D) -> None:
        # noinspection PyTypeChecker
        self._mesh_list.add(MeshCard(
            mesh,
            self._mesh_registry,
            edit_dialog_button=self._mesh_edit_dialog.create_edit_button(mesh),
            mesh_delete_button=Button().with_handler(
                lambda: self._dialog.begin(
                    f"Удалить '{mesh.name}'?",
                    on_confirm=lambda: self._mesh_registry.remove(mesh)
                )
            ),
        ))


class MeshPlotView(CustomWidget):

    def __init__(self, mesh: Mesh2D, plot: Container):
        self._mesh: Final = mesh
        self._plot: Final = plot

        self._translation_point: Final = DragPoint(_value=Vector2D(0, 0), _color=Color.gray(0.8))
        self._plot.add(self._translation_point)

        super().__init__(
            self._translation_point
            .with_handler(self._mesh.transformation.set_translation)
        )

        for t in self._mesh.trajectories.values():
            self._add_trajectory(t)

        self._mesh.trajectories.on_add.add_listener(self._add_trajectory)

        self._update_name(self._mesh.name)
        self._mesh.on_name_changed.add_listener(self._update_name)

        self._update_transformation(self._mesh.transformation)
        self._mesh.transformation.on_change.add_listener(self._update_transformation)

    def _add_trajectory(self, trajectory: Trajectory) -> None:
        line_series = LineSeries(_value=(list(), list()))
        self._plot.add(line_series)

        def _update(transformation: Transformation2D):
            line_series.set_value(trajectory.transformed(transformation.apply))

        self._mesh.transformation.on_change.add_listener(_update)

        _update(self._mesh.transformation)

        def _remove(__t: Trajectory):
            if __t is not trajectory:
                return

            self._mesh.transformation.on_change.remove_listener(_update)
            self._mesh.trajectories.on_remove.remove_listener(_remove)
            line_series.delete()

        self._mesh.trajectories.on_remove.add_listener(_remove)

    def _update_name(self, name: str) -> None:
        self._translation_point.set_label(name)

    def _update_transformation(self, transformation: Transformation2D) -> None:
        self._translation_point.set_value(transformation.translation)

    def terminate(self, mesh: Mesh2D) -> None:
        if mesh is not self._mesh:
            return

        self.delete()

    def delete(self) -> None:
        self._mesh.on_name_changed.remove_listener(self._update_name)
        self._mesh.transformation.on_change.remove_listener(self._update_transformation)
        self._mesh.trajectories.on_add.remove_listener(self._add_trajectory)
        super().delete()


class WorkArea(CustomWidget):

    def __init__(self, mesh_registry: MeshRegistry):
        self._mesh_registry: Final = mesh_registry
        self._plot: Final = Plot()

        super().__init__(
            self._plot
            .with_width(-1)
            .with_height(-1)
        )

        for mesh in self._mesh_registry.values():
            self._add_mesh_plot_item(mesh)

        self._mesh_registry.on_add.add_listener(self._add_mesh_plot_item)

    def _add_mesh_plot_item(self, mesh: Mesh2D) -> None:
        view = MeshPlotView(mesh, self._plot)
        self._mesh_registry.on_remove.add_listener(view.terminate)


class PreparingView(CustomWidget):
    def __init__(self, mesh_registry: MeshRegistry):
        super().__init__(
            HBox()
            .add(MeshList(mesh_registry))
            .add(WorkArea(mesh_registry))
        )

        self._log: Final = Logger(self.__class__.__name__)
