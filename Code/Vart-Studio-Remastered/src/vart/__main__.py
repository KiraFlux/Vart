import vart.boot
from vart.detail.mesh import MeshRegistry, Mesh2D

vart.boot.attach_libs()

from kf_dpg.impl.containers import Window
from vart.ui.app import VartApplication
from vart.ui.views.config import ConfigView
from vart.ui.views.jornal import JornalView
from vart.ui.views.prepare import PreparingView


def _launch():
    mesh_registry = MeshRegistry()

    mesh_registry.add(Mesh2D((), (), name="Test"))

    app = VartApplication(
        Window(),
        (
            ("Подготовка", PreparingView(mesh_registry)),
            ("Параметры", ConfigView()),
            ("Журнал", JornalView()),
        )
    )

    app.run(
        vart.boot.project_name,
        1280, 720,
        user_tasks=()
    )

    return


if __name__ == '__main__':
    _launch()
