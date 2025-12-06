import numpy as np
from pySimBlocks.core.block import Block


class DiscreteIntegrator(Block):
    """
    Discrete-time integrator.

    Description:
        Implements:
            x[k+1] = x[k] + dt * in[k]
            out[k] = x[k]

        Supported integration method:
            - 'euler forward'
            - 'euler backward'
        (default = 'euler forward')

    Parameters:
        name: str
            Block name.

        initial_state: float | array-like (n,) | array (n,1) (optional)
            Initial value of the integrated state x[0]. (default = zeros)
            If None:
                - If input is known at initialization → x[0] = zeros of the same dimension
                - Otherwise dimension is inferred at the first step

        method: str (optional)
            Integration method. (default = 'euler forward')
            Supported:
                - 'euler forward'
                - 'euler backward'

    Inputs:
        in: array (n,1)
            Signal to integrate.

    Outputs:
        out: array (n,1)
            Current integrated state x[k].
    """

    def __init__(self,
        name: str,
        initial_state=None,
        method: str = "euler forward"
    ):
        super().__init__(name)

        # --------------------------- validate method
        self.method = method.lower()
        if self.method not in ("euler forward", "euler backward"):
            raise ValueError(
                f"[{self.name}] Unsupported method '{method}'. "
                f"Allowed: 'euler forward', 'euler backward'."
            )

        # --------------------------- ports
        self.inputs["in"] = None
        self.outputs["out"] = None

        # --------------------------- state
        if initial_state is not None:
            arr = np.asarray(initial_state)
            if arr.ndim == 0:
                arr = arr.reshape(1, 1)
            elif arr.ndim == 1:
                arr = arr.reshape(-1, 1)
            elif arr.ndim == 2 and arr.shape[1] == 1:
                pass
            else:
                raise ValueError(
                    f"[{self.name}] initial_state must be scalar or column vector (n,1). "
                    f"Got shape {arr.shape}."
                )
            self.state["x"] = arr.copy()
        else:
            self.state["x"] = None

        self.next_state["x"] = None
        self._dt = 0.0   # for backward Euler


    # ------------------------------------------------------------------
    def initialize(self, t0: float):
        """
        Initialize state x[0] and output.

        Rules:
        - If initial_state provided → use it
        - Else if input available → infer dimension and set x[0] = zeros
        - Else output stays None until dimension known
        """
        x = self.state["x"]
        u = self.inputs["in"]

        if x is not None:
            # Fully initialized
            self.outputs["out"] = x.copy()
            self.next_state["x"] = x.copy()
            return

        # Input already present → infer dimension
        if u is not None:
            u = np.asarray(u)
            if u.ndim != 2 or u.shape[1] != 1:
                raise ValueError(
                    f"[{self.name}] Input 'in' must be column vector (n,1). Got {u.shape}."
                )
            u = u.reshape(-1, 1)

            self.state["x"] = np.zeros_like(u)
            self.outputs["out"] = self.state["x"].copy()
            self.next_state["x"] = self.state["x"].copy()
            return

        # Dimension unknown → output not ready
        self.outputs["out"] = None


    # ------------------------------------------------------------------
    def output_update(self, t: float):
        x = self.state["x"]
        if x is None:
            raise RuntimeError(f"[{self.name}] State not initialized.")

        u = self.inputs["in"]
        if u is None:
            raise RuntimeError(f"[{self.name}] Input 'in' not set.")

        # Euler forward simply outputs x[k]
        if self.method == "euler forward":
            self.outputs["out"] = x.copy()

        # Euler backward outputs x[k] + dt * u[k]
        else:
            u = np.asarray(u)
            if u.ndim != 2 or u.shape[1] != 1:
                raise ValueError(
                    f"[{self.name}] Input 'in' must be column vector (n,1). Got {u.shape}."
                )
            u = u.reshape(-1, 1)

            if u.shape != x.shape:
                raise ValueError(
                    f"[{self.name}] Input has shape {u.shape}, but state has shape {x.shape}."
                )

            self.outputs["out"] = x + self._dt * u


    # ------------------------------------------------------------------
    def state_update(self, t: float, dt: float):
        """
        Update internal state:
            Euler forward  : x[k+1] = x[k] + dt * u[k]
            Euler backward : x[k+1] = x[k] + dt * u[k]
            (same formula, difference is only in output_update)
        """
        u = self.inputs["in"]
        if u is None:
            raise RuntimeError(f"[{self.name}] Input 'in' not set.")

        u = np.asarray(u)
        if u.ndim != 2 or u.shape[1] != 1:
            raise ValueError(
                f"[{self.name}] Input 'in' must be column vector (n,1). Got {u.shape}."
            )
        u = u.reshape(-1, 1)

        x = self.state["x"]

        if x is not None:
            if u.shape != x.shape:
                raise ValueError(
                    f"[{self.name}] Input has dimension {u.shape}, "
                    f"but state has dimension {x.shape}."
                )

        # 3) Late initialization ONLY if x was truly never set
        if x is None:
            # Late dimension inference
            x = np.zeros_like(u)

        self._dt = dt
        self.next_state["x"] = x + dt * u
