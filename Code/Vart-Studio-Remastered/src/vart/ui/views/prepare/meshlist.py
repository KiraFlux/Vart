from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.etc.dialog import EditDialog, ConfirmDialog
from kf_dpg.etc.input2d import FloatInput2D
from kf_dpg.impl.boxes import TextInput, IntInput
from kf_dpg.impl.buttons import Button
from kf_dpg.impl.containers import VBox, ChildWindow, HBox
from kf_dpg.impl.text import Text
from kf_dpg.misc.color import Color
from vart.assets import Assets
from vart.detail.mesh import Mesh, MeshRegistry


class MeshEditDialog(EditDialog):

    @classmethod
    def _get_title(cls, mesh: Mesh) -> str:
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
        confirm_dialog: Final = ConfirmDialog().with_font(Assets.default_font)
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
                    lambda: confirm_dialog.begin(
                        f"Удалить {len(mesh_registry.values())} эл.?",
                        on_confirm=mesh_registry.clear
                    )
                )
            )
            .add(mesh_list)
        )

        def add_mesh_card(mesh: Mesh) -> None:
            edit_dialog: Final = MeshEditDialog().with_font(Assets.default_font)

            # noinspection PyTypeChecker
            mesh_list.add(MeshView(
                mesh,
                mesh_registry,
                edit_dialog_button=edit_dialog.create_edit_button(mesh),
                mesh_delete_button=Button().with_handler(
                    lambda: confirm_dialog.begin(
                        f"Удалить '{mesh.name}'?",
                        on_confirm=lambda: mesh_registry.remove(mesh)
                    )
                ),
            ))

        for __m in mesh_registry.values():
            add_mesh_card(__m)

        mesh_registry.on_add.add_listener(add_mesh_card)
