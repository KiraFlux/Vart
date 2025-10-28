from dataclasses import dataclass
from math import hypot
from typing import Optional
from typing import TextIO

from gen.enums import MarkerTool
from gen.enums import PlannerMode
from gen.movementprofile import MovementProfile
from gen.settings import GeneratorSettings


@dataclass(frozen=True)
class LowLevelAgent:
    """Низкоуровневый агент"""

    _stream: TextIO
    """Используемый поток для вывода"""

    def prelude(self) -> None:
        """Записать прелюдию"""
        self._write(".env vart_esp32")

    def comment(self, message: str) -> None:
        """Добавить информативный коментарий"""
        self._write(f"# {f"<<< {message} >>>":-^80} #")

    def note(self, message: str) -> None:
        """Добавить заметку"""
        self._write(f"# Note: {message}")

    def quit(self) -> None:
        """завершить работу"""
        self._write("quit")

    def delay_ms(self, ms: int) -> None:
        """Временная задержка"""
        self._write(f"delay_ms {ms}")

    def set_speed(self, speed: int) -> None:
        """Установить скорость перемещения"""
        self._write(f"set_speed {speed}")

    def set_accel(self, accel: int) -> None:
        """Установить ускорение"""
        self._write(f"set_accel {accel}")

    def set_planner_mode(self, mode: PlannerMode) -> None:
        """Установить режим планировщика"""
        self._write(f"set_planner_mode {int(mode)}")

    def set_position(self, x: int, y: int) -> None:
        """Установить (Переместиться) позицию"""
        self._write(f"set_position {x} {y}")

    def set_progress(self, progress: int) -> None:
        """Установить значение прогресса"""
        self._write(f"set_progress {progress}")

    def set_active_tool(self, tool: MarkerTool) -> None:
        """Установить активный инструмент"""
        self._write(f"set_active_tool {int(tool)}")

    def _write(self, ins: str) -> None:
        self._stream.write(f"{ins}\n")


@dataclass
class MacroAgent:
    """Макро Агент"""

    _agent: LowLevelAgent
    """Используемый агент"""

    _settings: GeneratorSettings
    """Настройки генератора"""

    _steps_total: int
    """Общее число шагов"""

    _current_step: int = 0
    """Номер текущего шага"""

    _last_progress: int = -1
    """Предыдущее значение прогресса печати"""

    _last_profile: Optional[MovementProfile] = None
    """Предыдущий профиль перемещения"""

    _last_tool: Optional[MarkerTool] = None
    """Предыдущий цвет маркера"""

    def note(self, message: str) -> None:
        """Заметка"""
        self._agent.note(message)

    def prologue(self) -> None:
        """Сгенерировать прелюдию"""
        self._agent.comment("Prologue - Begin")
        self._agent.prelude()
        self._agent.note("Prologue - End")

    def setProfile(self, profile: MovementProfile) -> None:
        """Установить профиль планировщика"""
        self._agent.comment(f"Set Profile: {profile.name}")

        if self._last_profile == profile:
            self._agent.note("Skip (Same preset already active)")
            return

        self._last_profile = profile
        self._agent.set_speed(profile.speed)
        self._agent.set_accel(profile.accel)
        self._agent.set_planner_mode(profile.mode)

    def setTool(self, tool: MarkerTool) -> None:
        """Установить инструмент для печати"""
        self._agent.comment(f"Set Tool: {tool}")

        if self._last_tool == tool:
            self._agent.note("Skip (Same color already active)")
            return

        self._last_tool = tool
        self._agent.delay_ms(self._settings.tool_change_begin_timeout_ms)
        self._agent.set_active_tool(tool)
        self._agent.delay_ms(self._settings.tool_change_end_timeout_ms)

    def step(self, x: int, y: int) -> None:
        """Сделать шаг (Перейти в позицию)"""
        self._current_step += 1
        self._agent.set_position(x, y)

        current_progress = self._current_step * 100 // self._steps_total
        if current_progress != self._last_progress:
            self._last_progress = current_progress
            self._agent.note(f"Progress: {current_progress}")
            self._agent.set_progress(current_progress)

    def epilogue(self) -> None:
        """Сгенерировать эпилог"""
        self._agent.comment("Epilogue - Begin")
        self._agent.delay_ms(self._settings.epilogue_stop_duration_ms)
        x, y = self._settings.epilogue_end_position
        self._agent.set_position(x, y)
        self._agent.quit()
        self._agent.note("Epilogue - End")
