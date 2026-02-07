from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.core.dpg.plot import Plot, DragPoint
from kf_dpg.etc.dialog import EditDialog, ConfirmDialog
from kf_dpg.etc.input2d import FloatInput2D
from kf_dpg.impl.boxes import TextInput
from kf_dpg.impl.buttons import Button
from kf_dpg.impl.containers import VBox, ChildWindow, HBox
from kf_dpg.impl.misc import Spacer
from kf_dpg.impl.sliders import IntSlider
from kf_dpg.impl.text import Text
from kf_dpg.misc.color import Color
from kf_dpg.misc.vector import Vector2D
from vart.assets import Assets
from vart.detail.mesh import Mesh2D, MeshRegistry, Transformation2D
from vart.misc.log import Logger


class MeshEditDialog(EditDialog):

    @classmethod
    def _get_title(cls, mesh: Mesh2D) -> str:
        return f"Edit: '{mesh.name}'"

    def __init__(self):
        self._name: Final = TextInput().with_label("Наименование")

        self._rotation: Final = IntSlider("Поворот", interval=(0, 360))

        self._scale: Final = FloatInput2D(
            "Масштаб",
            interval=(-10000, 10000),
        )

        self._translation: Final = FloatInput2D(
            "Позиция",
            interval=(-10000, 10000),
        )

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
        self._rotation.set_value(mesh.transformation.rotation)
        self._scale.set_value(mesh.transformation.scale)
        self._translation.set_value(mesh.transformation.translation)

    def apply(self, mesh: Mesh2D) -> None:
        mesh.name = self._name.get_value()
        mesh.transformation.rotation = self._rotation.get_value()
        mesh.transformation.scale = self._scale.get_value()
        mesh.transformation.translation = self._translation.get_value()


class MeshCard(CustomWidget):

    def __init__(self, mesh: Mesh2D, edit_dialog_button: Button, mesh_delete_button: Button) -> None:
        self._target_mesh: Final = mesh

        self._name: Final = Text(color=Color.discord_success())
        self._target_mesh.on_name_changed.add_listener(self._name.set_value)

        super().__init__(
            ChildWindow()
            .with_height(80)
            .add(
                VBox()
                .add(self._name)
                .add(
                    HBox()
                    .add(
                        edit_dialog_button
                        .with_label("···")
                    )
                    .add(
                        mesh_delete_button
                        .with_label(" x ")
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

    def __init__(self, mesh_registry: MeshRegistry) -> None:
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
                .with_handler(lambda: self._mesh_registry.add(Mesh2D(())))
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
        card = MeshCard(
            mesh,
            self._mesh_edit_dialog.create_edit_button(mesh),
            Button().with_handler(
                lambda: self._dialog.begin(
                    f"Удалить '{mesh.name}'?",
                    on_confirm=lambda: self._mesh_registry.remove(mesh)
                )
            )
        )

        self._mesh_registry.on_remove.add_listener(card.terminate)
        self._mesh_list.add(card)


class MeshPlotView(CustomWidget):

    def __init__(self, mesh: Mesh2D):
        self._mesh: Final = mesh
        self.translation_point: Final = DragPoint(_value=Vector2D(0, 0), _color=Color.gray(0.8))

        self._mesh.on_name_changed.add_listener(self._update_name)
        self._mesh.transformation.on_change.add_listener(self._update_transformation)

        super().__init__(
            self.translation_point
            .with_handler(self._mesh.transformation.set_translation)
        )

        self._update_name(self._mesh.name)
        self._update_transformation(self._mesh.transformation)

    def _update_name(self, name: str) -> None:
        self.translation_point.set_label(name)

    def _update_transformation(self, transformation: Transformation2D) -> None:
        self.translation_point.set_value(transformation.translation)

    def terminate(self, mesh: Mesh2D) -> None:
        if mesh is not self._mesh:
            return

        self.delete()

    def delete(self) -> None:
        self._mesh.on_name_changed.remove_listener(self._update_name)
        self._mesh.transformation.on_change.remove_listener(self._update_transformation)
        super().delete()


class WorkArea(CustomWidget):

    def __init__(self, mesh_registry: MeshRegistry) -> None:
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
        view = MeshPlotView(mesh)
        self._mesh_registry.on_remove.add_listener(view.terminate)
        self._plot.add(view.translation_point)


class PreparingView(CustomWidget):
    def __init__(self, mesh_registry: MeshRegistry) -> None:
        super().__init__(
            HBox()
            .add(MeshList(mesh_registry))
            .add(WorkArea(mesh_registry))
        )

        self._log: Final = Logger(self.__class__.__name__)
