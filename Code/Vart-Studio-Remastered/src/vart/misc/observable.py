from typing import Iterable, Final, AbstractSet

from kf_dpg.misc.subject import Subject
from vart.misc.log import Logger


class ObservableRegistry[T]:

    def __init__(self, init: Iterable[T] = ()):
        self.on_add: Final = Subject[T]()
        self.on_remove: Final = Subject[T]()
        self._items: Final = set[T](init)

        self._log: Final = Logger(f"{self.__class__.__name__}@{id(self)}")

    def add(self, item: T) -> None:
        self._log.write(f"add: {item!r}")
        self._items.add(item)
        self.on_add.notify(item)

    def remove(self, item: T) -> None:
        self._log.write(f"remove: {item!r}")
        self._items.remove(item)
        self.on_remove.notify(item)

    def clear(self) -> None:
        self._log.write(f"clear")

        for item in tuple(self._items):
            self.remove(item)

        self._items.clear()

    def values(self) -> AbstractSet[T]:
        return self._items
