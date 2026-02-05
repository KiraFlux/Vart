import math
from typing import Final

from kf_dpg.core.custom import CustomWidget
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
        self._target_mesh.on_change.addListener(self._update)

        self._text: Final = Text(color=Color.online())
        self._rotation: Final = IntSlider("Поворот", interval=(0, 360))

        super().__init__(
            ChildWindow()
            .withHeight(100)
            .add(
                VBox()
                .add(self._text)
                .add(
                    Button()
                    .withLabel("Удалить")
                    .withHandler(self.delete)
                )
                .add(
                    self._rotation
                    .withHandler(lambda d: self._target_mesh.set_rotation(math.radians(d)))
                )
            )
        )

        self._update(mesh)

    def _update(self, mesh: Mesh2D) -> None:
        self._text.setValue(str(mesh))
        self._rotation.setValue(math.degrees(mesh.rotation))

    def delete(self) -> None:
        self._target_mesh.on_change.removeListener(self._update)
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
                .withLabel("Добавить")
                .withWidth(-1)
                .withHandler(lambda: self._mesh_registry.add(Mesh2D((), ())))
            )
            .add(
                self._mesh_list
            )
        )

        for mesh in self._mesh_registry.get_all():
            self._add_mesh_card(mesh)

        self._mesh_registry.on_add.addListener(self._add_mesh_card)

    def _add_mesh_card(self, mesh: Mesh2D) -> None:
        card = MeshCard(mesh)
        card.attachDeleteObserver(lambda _: self._mesh_registry.remove(mesh))
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
