import numpy as np
from pySimBlocks.core.block import Block


class RateLimiter(Block):
    """
    Discrete-time rate limiter.

    Description:
        Limits the rate of change of the output signal between two consecutive
        time steps. Rising and falling slopes can be specified independently.
        Initial_output defines y[-1]. If omitted, y[-1] = u(0).

        Discrete rate limiter:
            delta = u[k] - y[k-1]
            y[k] = y[k-1] + clip(delta, -falling_slope*dt, rising_slope*dt)

    Parameters:
        name: str
            Block name.

        rising_slope: float | array-like (n,) | array (n,1)
            Maximum allowed positive rate of change (units per second).

        falling_slope: float | array-like (n,) | array (n,1)
            Maximum allowed negative rate of change (units per second).

        initial_output: float | array-like (n,) | array (n,1) (optional)
            Initial output value y[0].
            If not provided, the first input value is used. (default = None)

    Inputs:
        in: array (n,1)
            Input signal u[k].

    Outputs:
        out: array (n,1)
            Rate-limited output signal y[k].
    """

    def __init__(self,
                 name: str,
                 rising_slope,
                 falling_slope,
                 initial_output=None):

        super().__init__(name)

        self.inputs["in"] = None
        self.outputs["out"] = None

        # Normalize slopes to column vectors
        self.rising_slope = self._to_column("rising_slope", rising_slope)
        self.falling_slope = self._to_column("falling_slope", falling_slope)

        if np.any(self.rising_slope < 0):
            raise ValueError(f"[{self.name}] rising_slope must be >= 0.")
        if np.any(self.falling_slope > 0):
            raise ValueError(f"[{self.name}] falling_slope must be <= 0.")

        # Optional initial output
        self.initial_output = None
        if initial_output is not None:
            self.initial_output = self._to_column("initial_output", initial_output)

        # Internal state
        self.state["y"] = None
        self.next_state["y"] = None

        self._dt = 0.

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _to_column(self, name, value):
        arr = np.asarray(value)

        if arr.ndim == 0:
            return arr.reshape(1, 1)
        elif arr.ndim == 1:
            return arr.reshape(-1, 1)
        elif arr.ndim == 2 and arr.shape[1] == 1:
            return arr
        else:
            raise ValueError(
                f"[{self.name}] '{name}' must be scalar or vector, got shape {arr.shape}."
            )

    def _broadcast(self, ref, target):
        """
        Broadcast scalar (1,1) to match ref dimension if needed.
        """
        if target.shape[0] == 1 and ref.shape[0] > 1:
            return np.full_like(ref, target.item())
        return target

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialize(self, t0: float):
        u = self.inputs["in"]

        if u is None:
            raise RuntimeError(f"[{self.name}] Input 'in' is None at initialization.")

        u = self._to_column("input", u)

        # Broadcast slopes to input dimension
        self.rising_slope = self._broadcast(u, self.rising_slope)
        self.falling_slope = self._broadcast(u, self.falling_slope)

        if self.initial_output is not None:
            y0 = self._broadcast(u, self.initial_output)
        else:
            y0 = u.copy()

        self.state["y"] = y0
        self.outputs["out"] = y0


    def output_update(self, t: float):
        u = self.inputs["in"]
        if u is None:
            raise RuntimeError(f"[{self.name}] Input 'in' is None.")

        u = self._to_column("input", u)
        y_prev = self.state["y"]

        du = u - y_prev

        max_up = self.rising_slope * self._dt
        max_down = self.falling_slope * self._dt

        du_limited = np.where(
            du > 0,
            np.minimum(du, max_up),
            np.maximum(du, max_down),
        )

        y = y_prev + du_limited
        self.outputs["out"] = y


    def state_update(self, t: float, dt: float):
        self._dt = dt
        self.next_state["y"] = self.outputs["out"]
