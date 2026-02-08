from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.etc.dialog import EditDialog, ConfirmDialog
from kf_dpg.etc.input2d import FloatInput2D
from kf_dpg.impl.boxes import TextInput, IntInput
from kf_dpg.impl.buttons import Button, CheckBox
from kf_dpg.impl.containers import VBox, ChildWindow, HBox, Tab, TabBar
from kf_dpg.impl.misc import Spacer
from kf_dpg.impl.text import Text
from kf_dpg.misc.color import Color
from vart.assets import Assets
from vart.core.mesh import Mesh, MeshRegistry
from vart.core.trajectory import Trajectory


class TrajectoryView(CustomWidget):
    """
    Карточка просмортра и редактирования трактории
    """

    def __init__(self, mesh_registry: MeshRegistry, mesh: Mesh, trajectory: Trajectory) -> None:
        loop = CheckBox(_value=trajectory.loop)
        tool_id = IntInput(interval_min=0, interval_max=99)

        tab = Tab()

        super().__init__(
            tab
            .add(
                HBox()
                .add(
                    VBox()
                    .with_width(200)
                    .add(
                        loop
                        .with_label("Замкнутый")
                        .with_handler(trajectory.set_loop)
                    )
                    .add(
                        tool_id
                        .with_label("Инструмент")
                        .with_handler(trajectory.set_tool_id)
                    )
                )
                .add(Spacer().with_height(50))
                .add(
                    VBox()
                    .with_width(200)
                    .add(
                        Button()
                        .with_width(-1)
                        .with_label("Удалить")
                        .with_handler(lambda: mesh.trajectories.remove(trajectory))
                    )
                    .add(
                        Button()
                        .with_width(-1)
                        .with_label("Отделить")
                        .with_handler(lambda: mesh_registry.add_extracted_trajectory(mesh, trajectory))
                    )
                )
            )
        )

        def update_name(new_name: str):
            tab.set_label(new_name)

        update_name(trajectory.name)
        trajectory.on_name_changed.add_listener(update_name)

        def remove(__t: Trajectory) -> None:
            if __t is trajectory:
                self.attach_delete_observer(lambda _: trajectory.on_name_changed.add_listener(update_name))
                self.attach_delete_observer(lambda _: mesh.trajectories.on_remove.remove_listener(remove))
                self.delete()

        mesh.trajectories.on_remove.add_listener(remove)


class MeshEditDialog(EditDialog):

    @classmethod
    def _get_title(cls, mesh: Mesh) -> str:
        return f"Edit: '{mesh.name}'"

    def __init__(self, mesh_registry: MeshRegistry):
        self._mesh_registry: Final = mesh_registry
        self._name: Final = TextInput()
        self._rotation: Final = IntInput(step_fast=15, step=5).with_interval((-360, 360))
        self._scale: Final = FloatInput2D(step=0.25, step_fast=1.0).with_interval((-10000, 10000))
        self._translation: Final = FloatInput2D(step=10, step_fast=100).with_interval((-10000, 10000))

        self._trajectories_container: Final = TabBar()
        self._trajectory_views: Final = set[TrajectoryView]()

        super().__init__(
            TabBar()
            .add(
                Tab()
                .with_label("Меш")
                .add(self._name.with_label("Наименование"))
                .add(self._rotation.with_label("Поворот"))
                .add(self._scale.with_label("Масштаб"))
                .add(self._translation.with_label("Позиция"))
            )
            .add(
                Tab()
                .with_label("Траектории")
                .add(
                    self._trajectories_container
                )
            )
        )
        self.set_width(1200)
        self.set_height(800)

    def begin(self, mesh: Mesh) -> None:
        super().begin(mesh)

        self._name.set_value(mesh.name)
        self._name.set_handler(mesh.set_name)

        self._rotation.set_value(mesh.transformation.get_rotation_degrees())
        self._rotation.set_handler(mesh.transformation.set_rotation_degrees)

        self._scale.set_value(mesh.transformation.scale)
        self._scale.set_handler(mesh.transformation.set_scale)

        self._translation.set_value(mesh.transformation.translation)
        self._translation.set_handler(mesh.transformation.set_translation)

        for __t in self._trajectory_views:
            __t.delete()

        def add_trajectory_view(trajectory: Trajectory):
            view = TrajectoryView(self._mesh_registry, mesh, trajectory)
            self._trajectory_views.add(view)
            # noinspection PyTypeChecker
            self._trajectories_container.add(view)

        for __t in mesh.trajectories.values():
            add_trajectory_view(__t)


class MeshView(CustomWidget):

    def __init__(
            self, mesh: Mesh,
            mesh_registry: MeshRegistry,
            *,
            edit_dialog_button: Button,
            mesh_delete_button: Button,
    ):
        name_display: Final = Text(color=Color.discord_success())

        super().__init__(
            ChildWindow()
            .with_height(80)
            .add(
                VBox()
                .add(name_display)
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

        mesh.on_name_changed.add_listener(name_display.set_value)
        name_display.set_value(mesh.name)
        self.attach_delete_observer(lambda _: mesh.on_name_changed.remove_listener(name_display.set_value))

        def remove(__m: Mesh) -> None:
            if __m is mesh:
                self.delete()

        mesh_registry.on_remove.add_listener(remove)


class MeshRegistryView(CustomWidget):

    def __init__(self, mesh_registry: MeshRegistry):
        self._confirm_dialog: Final = ConfirmDialog().with_font(Assets.default_font)
        self._edit_dialog: Final = MeshEditDialog(mesh_registry).with_font(Assets.default_font)

        mesh_list: Final = ChildWindow(scrollable_y=True)

        super().__init__(
            VBox()
            .with_width(400)
            .add(
                Button()
                .with_label("Добавить")
                .with_width(-1)
                .with_handler(mesh_registry.add_dummy)
            )
            .add(
                Button()
                .with_label("Очистить")
                .with_width(-1)
                .with_handler(
                    lambda: self._confirm_dialog.begin(
                        f"Удалить {len(mesh_registry.values())} эл.?",
                        on_confirm=mesh_registry.clear
                    )
                )
            )
            .add(mesh_list)
        )

        def add_mesh_card(mesh: Mesh) -> None:
            # noinspection PyTypeChecker
            mesh_list.add(MeshView(
                mesh,
                mesh_registry,
                edit_dialog_button=Button().with_handler(
                    lambda: self._edit_dialog.begin(mesh)
                ).with_label("···"),
                mesh_delete_button=Button().with_handler(
                    lambda: self._confirm_dialog.begin(
                        f"Удалить '{mesh.name}'?",
                        on_confirm=lambda: mesh_registry.remove(mesh)
                    )
                ),
            ))

        for __m in mesh_registry.values():
            add_mesh_card(__m)

        mesh_registry.on_add.add_listener(add_mesh_card)
