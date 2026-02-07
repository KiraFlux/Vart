from abc import ABC, abstractmethod

from vart.detail.mesh import Mesh


class Importer(ABC):

    @abstractmethod
    def import_mesh(self) -> Mesh:
        """Импортироать меш"""
