import numpy as np
from pySimBlocks.core.block import Block


class BlockSource(Block):
    """
    Base class for all source blocks (Constant, Step, Ramp, Sinusoidal, ...).

    Provides:
        - normalization utilities for source parameters to produce 2D signals
        - strict scalar-only broadcasting to a common 2D shape
        - no state update by default
    """

    direct_feedthrough = False
    is_source = True

    def __init__(self, name: str, sample_time: float | None = None):
        super().__init__(name, sample_time)

    # ------------------------------------------------------------------
    # Core normalization: always returns a 2D ndarray
    # ------------------------------------------------------------------
    def _to_2d_array(self, param_name: str, value, *, dtype=float) -> np.ndarray:
        """
        Normalize into a 2D NumPy array.

        Rules:
            - scalar -> (1,1)
            - 1D -> (n,1) (column vector convention)
            - 2D -> preserved as-is (m,n)
            - ndim > 2 -> rejected
        """
        arr = np.asarray(value, dtype=dtype)

        if arr.ndim == 0:
            return arr.reshape(1, 1)

        if arr.ndim == 1:
            return arr.reshape(-1, 1)

        if arr.ndim == 2:
            return arr

        raise ValueError(
            f"[{self.name}] '{param_name}' must be scalar, 1D, or 2D array-like. "
            f"Got ndim={arr.ndim} with shape {arr.shape}."
        )

    # ------------------------------------------------------------------
    # Strict scalar-only broadcast policy (Option B)
    # ------------------------------------------------------------------
    @staticmethod
    def _is_scalar_2d(arr: np.ndarray) -> bool:
        return arr.shape == (1, 1)

    def _resolve_common_shape(self, params: dict[str, np.ndarray]) -> tuple[int, int]:
        """
        Determine the common target shape among parameters.

        Policy:
            - scalars (1,1) are broadcastable
            - any non-scalar (2D not (1,1)) fixes the target shape
            - if multiple non-scalars exist, all must have exactly the same shape
            - if all are scalars -> target shape is (1,1)
        """
        non_scalar_shapes = {a.shape for a in params.values() if not self._is_scalar_2d(a)}

        if len(non_scalar_shapes) == 0:
            return (1, 1)

        if len(non_scalar_shapes) == 1:
            return next(iter(non_scalar_shapes))

        details = ", ".join(f"{k}={v.shape}" for k, v in params.items())
        raise ValueError(
            f"[{self.name}] Inconsistent parameter shapes. "
            f"All non-scalar parameters must have the same (m,n) shape. Got: {details}"
        )

    def _broadcast_scalar_only(self, param_name: str, arr: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
        """
        Broadcast only scalar (1,1) to target_shape.
        Any non-scalar must already match target_shape exactly.
        """
        if self._is_scalar_2d(arr):
            if target_shape == (1, 1):
                return arr.astype(float, copy=False)
            return np.full(target_shape, float(arr[0, 0]), dtype=float)

        if arr.shape != target_shape:
            raise ValueError(
                f"[{self.name}] '{param_name}' shape {arr.shape} is incompatible with "
                f"target shape {target_shape}. Only scalar-to-shape broadcasting is allowed."
            )

        return arr.astype(float, copy=False)

    # ------------------------------------------------------------------
    def state_update(self, t: float, dt: float) -> None:
        pass  # all sources are stateless
