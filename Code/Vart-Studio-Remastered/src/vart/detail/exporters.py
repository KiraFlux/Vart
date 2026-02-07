from abc import ABC, abstractmethod

from vart.detail.mesh import Mesh


class Exporter(ABC):

    @abstractmethod
    def export_mesh(self, mesh: Mesh) -> None:
        """Экспортировать меш"""
