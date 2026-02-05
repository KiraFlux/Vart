from __future__ import annotations

from typing import Callable, ClassVar, Iterable, MutableMapping, MutableSequence, Sequence

from kf_dpg.misc.subject import Subject


class Logger:
    _logs: ClassVar[MutableMapping[str, MutableSequence[tuple[int, str]]]] = dict()
    _writes: ClassVar = 0

    on_write: ClassVar = Subject()
    on_create: ClassVar = Subject()

    def __init__(self, key: str) -> None:
        self._key = key

        self.on_create.notify(key)

        self.write("created")

    @property
    def key(self) -> str:
        """Ключ канала лога"""
        return self._key

    def write(self, message: str) -> None:
        """Записать сообщение в лог"""

        out = self._logs.get(self._key)

        if out is None:
            out = self._logs[self._key] = list()

        out.append((
            self._writes,
            message
        ))

        self.__class__._writes += 1

        self.on_write.notify(None)

    @classmethod
    def get_keys(cls) -> Sequence[str]:
        """Получить все доступные ключи журнала"""
        return tuple(cls._logs.keys())

    @classmethod
    def get_by_filter(cls, keys: Sequence[str]) -> Iterable[str]:
        """Получить логи"""

        if len(keys) == 0:
            return ()

        def _get_message_deco_strategy() -> Callable[[str, str], str]:
            if len(keys) == 1:
                return lambda _, m: m

            padding = max(map(len, keys)) + 2
            return lambda __k, __m: f"{f"[{__k}]":{padding}} {__m}"

        entries = (
            (index, key, msg)
            for key in keys
            if key in cls._logs
            for index, msg in cls._logs[key]
        )

        message_decorator = _get_message_deco_strategy()

        sorted_entries = sorted(entries, key=lambda x: x[0])

        return (
            message_decorator(key, message)
            for _, key, message in sorted_entries
        )
