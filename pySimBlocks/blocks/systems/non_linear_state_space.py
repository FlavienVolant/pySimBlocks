import inspect
import importlib.util
from pathlib import Path
from typing import Callable, List, Dict

import numpy as np

from pySimBlocks.core.block import Block


class NonLinearStateSpace(Block):
    """
    User-defined algebraic function block.

    Summary:
        Stateless block defined by a user-provided Python function:
            x+ = f(t, dt, x, u1, u2, ...)
            y = g(t, dt)

    Parameters:
        file_path : str
            Path to the Python file containing the function (relative to project dir).
        state_function_name : str
            Name of the state function to call.
        output_function_name : str
            Name of the ouput function to call.
        input_keys : list[str]
            Names of input ports.
        output_keys : list[str]
            Names of output ports.
        sample_time : float, optional
            Block execution period.

    I/O:
        Inputs:
            Defined dynamically by input_keys.
        Outputs:
            Defined dynamically by output_keys.

    Notes:
        - This block is stateless.
        - Ports are fully declarative (V1).
        - The function must return a dict with exactly output_keys.
        - All inputs and outputs must be numpy arrays of shape (n,1).
    """

    direct_feedthrough = False
    is_source = False

    # ------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        file_path: str,
        state_function_name: str,
        output_function_name: str,
        input_keys: List[str],
        output_keys: List[str],
        sample_time: float | None = None,
    ):
        super().__init__(name=name, sample_time=sample_time)

        # ---- parameters
        self.file_path = Path(file_path)
        self.state_function_name = state_function_name
        self.output_function_name = output_function_name
        self.input_keys = list(input_keys)
        self.output_keys = list(output_keys)

        # ---- internals
        self._state_func: Callable | None = None
        self._output_func: Callable | None = None

        self.state["x"] = None
        self.next_state["x"] = None

    # ------------------------------------------------------------------
    def initialize(self, t0: float):
        """
        Load the user function and validate its signature.
        """
        self._load_function()
        self._validate_signature()

        # ---- declare ports
        for k in self.input_keys:
            self.inputs[k] = None

        for k in self.output_keys:
            # Initialized lazily at first output_update
            self.outputs[k] = None

    # ------------------------------------------------------------------
    def _load_function(self):
        """
        Load the Python function from file_path.
        """
        abs_path = Path(self.file_path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(
                f"{self.name}: file not found: {abs_path}"
            )

        spec = importlib.util.spec_from_file_location(
            abs_path.stem, abs_path
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                f"{self.name}: unable to load module from {abs_path}"
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        funcs = []
        for func_name in [self.state_function_name, self.output_function_name]:
            if not hasattr(module, func_name):
                raise AttributeError(
                    f"{self.name}: function '{func_name}' not found in {abs_path}"
                )

            func = getattr(module, func_name)
            if not callable(func):
                raise TypeError(
                    f"{self.name}: '{func_name}' is not callable"
                )
            funcs.append(func)

        self._state_func = funcs[0]
        self._output_func = funcs[1]

    # ------------------------------------------------------------------
    def _validate_signature(self):
        """
        Validate function signature against input_keys.
        """
        assert self._state_func is not None
        assert self._output_func is not None

        for f in [self._state_func, self._output_func]:
            sig = inspect.signature(f)
            params = list(sig.parameters.values())

            # ---- minimum signature: (t, dt, ...)
            if len(params) < 3:
                raise ValueError(
                    f"{self.name}: function must have at least arguments (t, dt, x)"
                )

            if params[0].name != "t" or params[1].name != "dt" or params[2].name != "x":
                raise ValueError(
                    f"{self.name}: first arguments must be (t, dt, x)"
                )

            # ---- no *args / **kwargs / defaults
            for p in params:
                if p.kind not in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ):
                    raise ValueError(
                        f"{self.name}: *args and **kwargs are not allowed"
                    )
                if p.default is not inspect.Parameter.empty:
                    raise ValueError(
                        f"{self.name}: default arguments are not allowed"
                    )

    # ------------------------------------------------------------------
    def output_update(self, t: float, dt: float):
        """
        Compute outputs from current inputs.
        """
        assert self._output_func is not None

        # ---- call function
        x = self.state["x"]
        out = self._output_func(t, dt, x=x)

        if not isinstance(out, dict):
            raise RuntimeError(
                f"{self.name}: function must return a dict"
            )

        if set(out.keys()) != set(self.output_keys):
            raise RuntimeError(
                f"{self.name}: output keys mismatch "
                f"(expected {self.output_keys}, got {list(out.keys())})"
            )

        # ---- assign outputs
        for k in self.output_keys:
            y = out[k]
            if not isinstance(y, np.ndarray):
                raise TypeError(
                    f"{self.name}: output '{k}' is not a numpy array"
                )
            if y.ndim != 2 or y.shape[1] != 1:
                raise ValueError(
                    f"{self.name}: output '{k}' must have shape (n,1)"
                )

            self.outputs[k] = y

    def state_update(self, t: float, dt: float):
        """
        Compute next state from current inputs.
        """
        assert self._output_func is not None

        # ---- collect inputs
        kwargs: Dict[str, np.ndarray] = {}
        for k in self.input_keys:
            u = self.inputs[k]
            if not isinstance(u, np.ndarray):
                raise TypeError(
                    f"{self.name}: input '{k}' is not a numpy array"
                )
            if u.ndim != 2 or u.shape[1] != 1:
                raise ValueError(
                    f"{self.name}: input '{k}' must have shape (n,1)"
                )
            kwargs[k] = u

        # ---- call function
        x = self.state["x"]
        out = self._state_func(t, dt, x=x, **kwargs)
        self.next_state["x"] = out
