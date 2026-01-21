
class ProjectSimulationParams:

    DEFAULT_DT = 0.1
    DEFAULT_SOLVER = "fixed"
    DEFAULT_T = 10.

    def __init__(
            self,
            dt: float = DEFAULT_DT,
            solver: str = DEFAULT_SOLVER,
            T: float = DEFAULT_T
    ):
        self.dt = dt
        self.solver = solver
        self.T = T

    def load_from_dict(self, params: dict) -> None:
        self.dt = params.get("dt", self.dt)
        self.solver = params.get("solver", self.solver)
        self.T = params.get("T", self.T)

    def clear(self) -> None:
        self.dt = self.DEFAULT_DT
        self.solver = self.DEFAULT_SOLVER
        self.T = self.DEFAULT_T