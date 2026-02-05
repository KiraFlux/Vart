import math
from typing import Final

from kf_dpg.core.custom import CustomWidget
from kf_dpg.etc.input2d import FloatInput2D
from kf_dpg.impl.buttons import Button
from kf_dpg.impl.containers import VBox, ChildWindow, HBox
from kf_dpg.impl.sliders import IntSlider
from kf_dpg.impl.text import Text
from kf_dpg.misc.color import Color
from vart.detail.mesh import Mesh2D, MeshRegistry
from vart.misc.log import Logger


class MeshCard(CustomWidget):

    def __init__(self, mesh: Mesh2D) -> None:
        self._target_mesh: Final = mesh
        self._target_mesh.on_change.add_listener(self._update)

        self._text: Final = Text(color=Color.discord_online())

        self._rotation: Final = IntSlider("Поворот", interval=(0, 360))

        self._scale: Final = FloatInput2D(
            "Масштаб",
            interval=(-10000, 10000),
            on_change=self._target_mesh.set_scale
        )

        self._translation: Final = FloatInput2D(
            "Позиция",
            interval=(-10000, 10000),
            on_change=self._target_mesh.set_translation
        )

        super().__init__(
            ChildWindow()
            .with_height(200)
            .add(
                VBox()
                .add(self._text)
                .add(
                    Button()
                    .with_label("X")
                    .with_handler(self.delete)
                )
                .add(
                    self._rotation
                    .with_handler(lambda d: self._target_mesh.set_rotation(math.radians(d)))
                )
                .add(
                    self._scale
                )
                .add(
                    self._translation
                )
            )
        )

        self._update(mesh)

    def _update(self, mesh: Mesh2D) -> None:
        self._text.set_value(mesh.name)
        self._rotation.set_value(math.degrees(mesh.rotation))
        self._scale.set_value(mesh.scale)
        self._translation.set_value(mesh.translation)

    def delete(self) -> None:
        self._target_mesh.on_change.remove_listener(self._update)
        super().delete()


class MeshList(CustomWidget):

    def __init__(self, mesh_registry: MeshRegistry) -> None:
        self._mesh_registry: Final = mesh_registry

        self._mesh_list: Final = ChildWindow(
            scrollable_y=True
        )

        super().__init__(
            VBox()
            .add(
                Button()
                .with_label("Добавить")
                .with_width(-1)
                .with_handler(lambda: self._mesh_registry.add(Mesh2D((), ())))
            )
            .add(
                self._mesh_list
            )
        )

        for mesh in self._mesh_registry.get_all():
            self._add_mesh_card(mesh)

        self._mesh_registry.on_add.add_listener(self._add_mesh_card)

    def _add_mesh_card(self, mesh: Mesh2D) -> None:
        card = MeshCard(mesh)
        card.attach_delete_observer(lambda _: self._mesh_registry.remove(mesh))
        self._mesh_list.add(card)


class PreparingView(CustomWidget):
    def __init__(self, mesh_registry: MeshRegistry) -> None:
        super().__init__(
            HBox()
            .add(
                MeshList(mesh_registry)
            )
        )

        self._log: Final = Logger(self.__class__.__name__)
