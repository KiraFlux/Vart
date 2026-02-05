from typing import Any
from typing import Callable


class Subject[T]:
    """Субъект"""

    def __init__(self) -> None:
        self.__observers = set[Callable[[T], Any]]()

    def notify(self, value: T) -> None:
        """Уведомить наблюдателей"""
        for observer in self.__observers:
            observer(value)

    def addListener(self, observer: Callable[[T], Any]) -> None:
        """Добавить наблюдателя"""
        self.__observers.add(observer)

    def removeListener(self, observer: Callable[[T], Any]):
        """Удалить наблюдателя"""
        self.__observers.remove(observer)
