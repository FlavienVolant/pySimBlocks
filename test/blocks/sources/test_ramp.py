import numpy as np
import pytest

from pySimBlocks.blocks.sources.ramp import Ramp


# ----------------------------------------------------------
# 1) Scalar slope and scalar start_time
# ----------------------------------------------------------
def test_ramp_scalar_before_start():
    r = Ramp("r", slope=2.0, start_time=1.0, offset=0.0)
    r.initialize(0.0)
    assert np.allclose(r.outputs["out"], [[0.0]])  # before start_time


def test_ramp_scalar_after_start():
    r = Ramp("r", slope=2.0, start_time=1.0, offset=0.0)
    r.output_update(2.0)
    assert np.allclose(r.outputs["out"], [[2.0]])  # slope * (2 - 1) = 2


# ----------------------------------------------------------
# 2) Vector parameters
# ----------------------------------------------------------
def test_ramp_vector_parameters():
    r = Ramp("r",
             slope=[1.0, 2.0],
             start_time=[0.0, 1.0],
             offset=[0.0, 10.0])
    r.output_update(2.0)
    # first: 1*(2-0)=2
    # second: 10 + 2*(2-1)=12
    assert np.allclose(r.outputs["out"], [[2.0], [12.0]])


# ----------------------------------------------------------
# 3) Broadcasting scalar to match vector dimension
# ----------------------------------------------------------
def test_ramp_broadcast_scalar_start_time():
    r = Ramp("r",
             slope=[1.0, 1.0, 1.0],
             start_time=0.0,
             offset=0.0)
    r.output_update(2.0)
    assert np.allclose(r.outputs["out"], [[2.0], [2.0], [2.0]])


# ----------------------------------------------------------
# 4) Inconsistent dimensions → error
# ----------------------------------------------------------
def test_ramp_inconsistent_dimensions():
    with pytest.raises(ValueError):
        Ramp("r",
             slope=[1.0, 2.0],
             start_time=[0.0, 1.0, 2.0],  # mismatch
             offset=[0.0, 1.0])


# ----------------------------------------------------------
# 5) Illegal shapes
# ----------------------------------------------------------
def test_ramp_illegal_matrix():
    with pytest.raises(ValueError):
        Ramp("r",
             slope=np.zeros((2, 2)),  # matrix → forbidden
             start_time=0.0,
             offset=0.0)
