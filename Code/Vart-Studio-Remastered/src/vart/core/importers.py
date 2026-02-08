from abc import ABC, abstractmethod

from vart.core.mesh import Mesh


class Importer(ABC):

    @abstractmethod
    def import_mesh(self) -> Mesh:
        """Импортироать меш"""
