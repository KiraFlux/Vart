from typing import Final

from vart.detail.workarea import WorkArea


class Config:
    """
    Конфигурация
    """

    def __init__(
            self,
            *,
            work_area: WorkArea
    ):
        self.work_area: Final = work_area
