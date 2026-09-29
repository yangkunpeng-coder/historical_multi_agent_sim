from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.simulation_engine import SimulationEngine
from core.world import World


@dataclass
class ScenarioRuntime:
    engine: SimulationEngine
    world: World


class Scenario(ABC):
    @abstractmethod
    def build(self) -> ScenarioRuntime:
        raise NotImplementedError

