from gen.movementprofile import MovementProfile
from gen.settings import GeneratorSettings
from ui.widgets.abc import ItemID
from ui.widgets.custom.input2d import InputInt2D
from ui.widgets.dpg.impl import CollapsingHeader
from ui.widgets.dpg.impl import InputInt
from ui.widgets.dpg.impl import SliderInt


class ProfileWidget(CollapsingHeader):

    def __init__(self, profile: MovementProfile) -> None:
        super().__init__(f"Параметры {profile.name}")
        self._profile = profile

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        speed_slider = SliderInt("Скорость (мм/с)", self._onSpeed, value_range=MovementProfile.SPEED_RANGE.asTuple(), default_value=self._profile.speed)
        accel_slider = SliderInt("Ускорение (мм/с^2)", self._onAccel, value_range=MovementProfile.ACCEL_RANGE.asTuple(), default_value=self._profile.accel)
        self.add(speed_slider).add(accel_slider)

    def _onSpeed(self, speed: int) -> None:
        self._profile.speed = speed

    def _onAccel(self, accel: int) -> None:
        self._profile.accel = accel


class CodeGeneratorSettngsWidget(CollapsingHeader):

    def __init__(self, settings: GeneratorSettings) -> None:
        super().__init__("Общие Настройки", default_open=True)
        self.settings = settings

    def _updateToolChangeBeginTimeout(self, x: int):
        self.settings.tool_change_begin_timeout_ms = x

    def _updateToolChangeEndTimeout(self, x: int):
        self.settings.tool_change_end_timeout_ms = x

    def _updateEpilogueStopDuration(self, x: int):
        self.settings.epilogue_stop_duration_ms = x

    def _updateEpilogueEndPosition(self, x: tuple[int, int]):
        self.settings.epilogue_end_position = x

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(ProfileWidget(self.settings.free_move_profile))
        self.add(ProfileWidget(self.settings.long_line_profile))
        self.add(ProfileWidget(self.settings.short_curve_profile))
        self.add(ProfileWidget(self.settings.micro_curve_profile))

        w = 400

        self.add(InputInt(
            "Тайм-аут перед сменой инструмента",
            self._updateToolChangeBeginTimeout,
            width=w, step=50, step_fast=100,
            default_value=self.settings.tool_change_begin_timeout_ms
        ))
        self.add(InputInt(
            "Тайм-аут После смены инструмента",
            self._updateToolChangeEndTimeout,
            width=w, step=50, step_fast=100,
            default_value=self.settings.tool_change_end_timeout_ms
        ))
        self.add(InputInt(
            "Тайм-аут Перед завершением рисования",
            self._updateEpilogueStopDuration,
            width=w, step=50, step_fast=100,
            default_value=self.settings.epilogue_stop_duration_ms
        ))
        self.add(InputInt2D(
            "Конечная позиция",
            self._updateEpilogueEndPosition,
            value_range=(-2000, 2000), input_width=w, reset_button=True,
            default_value=self.settings.epilogue_end_position
        ))
