from dataclasses import dataclass
from typing import BinaryIO
from typing import Iterable

from bytelang.compiler import ByteLangCompiler
from bytelang.core.results.compile.abc import CompileResult
from bytelang.tools.string import FixedStringIO
from bytelang.utils import LogFlag
from gen.agents import LowLevelAgent
from gen.agents import MacroAgent
from gen.settings import GeneratorSettings
from gen.trajectory import Trajectory


@dataclass
class CodeWriter:
    """Запись байткода"""

    _settings: GeneratorSettings
    _bytelang: ByteLangCompiler

    def run(self, trajectories: Iterable[Trajectory], bytecode_stream: BinaryIO, log_flag: LogFlag = LogFlag.ALL) -> CompileResult:
        stream = FixedStringIO()
        self._processAgent(MacroAgent(LowLevelAgent(stream), self._settings, self._calcTotalStepCount(trajectories)), trajectories)
        stream.seek(0)
        return self._bytelang.compile(stream, bytecode_stream, log_flag)

    def _processAgent(self, agent: MacroAgent, trajectories: Iterable[Trajectory]):
        agent.prologue()

        for trajectory in trajectories:
            trajectory.run(agent, self._settings)

        agent.epilogue()

    @staticmethod
    def _calcTotalStepCount(trajectories: Iterable[Trajectory]) -> int:
        return sum(t.vertexCount() for t in trajectories)
