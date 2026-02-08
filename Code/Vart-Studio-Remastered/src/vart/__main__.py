import vart.boot
from vart.core.config import Config

vart.boot.attach_libs()

from kf_dpg.impl.containers import Window, HBox

from vart.core.workarea import WorkArea
from vart.core.mesh import MeshRegistry
from vart.ui.app import VartApplication
from vart.ui.views.config import ConfigView
from vart.ui.views.jornal import JornalView
from vart.ui.views.prepare.workarea import WorkAreaView
from vart.ui.views.prepare.meshlist import MeshRegistryView


def _launch():
    config = Config(
        work_area=WorkArea(
            width=1000,
            height=1000
        )
    )

    mesh_registry = MeshRegistry()
    mesh_registry.add_dummy()

    app = VartApplication(
        Window(),
        (
            (
                "Подготовка",
                HBox()
                .add(MeshRegistryView(mesh_registry))
                .add(WorkAreaView(mesh_registry, config.work_area))
            ),
            (
                "Параметры",
                ConfigView()
            ),
            (
                "Журнал",
                JornalView()
            ),
        )
    )

    app.run(
        vart.boot.project_name,
        1280, 720,
        user_tasks=()
    )


if __name__ == '__main__':
    _launch()
