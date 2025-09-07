from __future__ import annotations

import math

import psutil
from qiskit_aer.primitives import SamplerV2 as Sampler

from .base_sampler_adapter import BaseSamplerAdapter


class AerSamplerAdapter(BaseSamplerAdapter):
    def __init__(self, sampler: Sampler | None = None):
        self.sampler = sampler or Sampler()

    @property
    def n_qubits(self) -> int:
        "Estimates the maximum number of qubits this computer can simulate"
        "considering the available memory and some rules of thumb"
        return int(math.log2(psutil.virtual_memory().available / 16))

    @property
    def t1s(self) -> dict[int, float]:
        "In an aer simulator, there is no limit on the t1."
        "It could be different if we include a noise model"
        return {qubit: float("inf") for qubit in range(self.n_qubits)}

    @property
    def t2s(self) -> dict[int, float]:
        "In an aer simulator, there is no limit on the t2."
        "It could be different if we include a noise model"
        return {qubit: float("inf") for qubit in range(self.n_qubits)}
