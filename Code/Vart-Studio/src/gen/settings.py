from dataclasses import dataclass

from gen.movementprofile import MovementProfile


@dataclass
class GeneratorSettings:
    """Настройки генератора"""

    free_move_profile: MovementProfile
    """Профиль перемещения без рисования (свободное перемещение)"""

    long_line_profile: MovementProfile
    """Профиль перемещения для рисования длинных линий (Полигоны и т.п.)"""

    short_curve_profile: MovementProfile
    """Профиль перемещения для рисования кривых (Множество точек рядом)"""

    micro_curve_profile: MovementProfile
    """Профиль для перемещения рисования малых отрезков"""

    tool_change_begin_timeout_ms: int
    """Пауза перед сменой инструмента"""

    tool_change_end_timeout_ms: int
    """Пауза после смены инструмента"""

    epilogue_stop_duration_ms: int
    """Длительность паузы после завершения печати"""

    epilogue_end_position: tuple[int, int]
    """Позиция после окончания печати"""

    def getProfileByIndex(self, index: int) -> MovementProfile:
        return (
            self.micro_curve_profile,
            self.short_curve_profile,
            self.long_line_profile
        )[index]
