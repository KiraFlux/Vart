from dataclasses import dataclass
from typing import BinaryIO, TextIO
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

    def run(self, ir_output_stream: TextIO, trajectories: Iterable[Trajectory], bytecode_stream: BinaryIO, log_flag: LogFlag = LogFlag.ALL) -> CompileResult:
        self._processAgent(MacroAgent(LowLevelAgent(ir_output_stream), self._settings, self._calcTotalStepCount(trajectories)), trajectories)
        with open(ir_output_stream.name, "rt") as ir_input:
            return self._bytelang.compile(ir_input, bytecode_stream, log_flag)

    def _processAgent(self, agent: MacroAgent, trajectories: Iterable[Trajectory]):
        agent.prologue()

        for trajectory in trajectories:
            trajectory.run(agent, self._settings)

        agent.epilogue()

    @staticmethod
    def _calcTotalStepCount(trajectories: Iterable[Trajectory]) -> int:
        return sum(t.vertexCount() for t in trajectories)
