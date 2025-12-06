import numpy as np
import pytest

from pySimBlocks.blocks.sources.sinusoidal import Sinusoidal


# ----------------------------------------------------------
# 1) Scalar parameters
# ----------------------------------------------------------
def test_sinusoidal_scalar():
    s = Sinusoidal("s", amplitude=2.0, frequency=1.0, offset=0.5, phase=0.0)
    s.initialize(0.0)
    assert np.allclose(s.outputs["out"], [[0.5]])  # sin(0)=0


def test_sinusoidal_scalar_time():
    s = Sinusoidal("s", 2.0, 1.0, 0.0, 0.0)
    s.output_update(0.25)  # sin(2π * 1 * 0.25) = sin(π/2) = 1
    assert np.allclose(s.outputs["out"], [[2.0]])


# ----------------------------------------------------------
# 2) Vector parameters
# ----------------------------------------------------------
def test_sinusoidal_vector():
    s = Sinusoidal(
        "s",
        amplitude=[1.0, 2.0],
        frequency=[1.0, 0.5],
        offset=[0.0, 10.0],
        phase=[0.0, np.pi/2],
    )
    s.output_update(0.0)
    # out(0): [0 + 0, 2*sin(pi/2)+10] = [0, 12]
    assert np.allclose(s.outputs["out"], [[0.0], [12.0]])


# ----------------------------------------------------------
# 3) Broadcasting scalar to vector
# ----------------------------------------------------------
def test_sinusoidal_broadcast_scalar():
    s = Sinusoidal("s",
                   amplitude=[1.0, 1.0, 1.0],
                   frequency=0.5,   # broadcast
                   offset=0.0,
                   phase=0.0)
    s.output_update(1.0)
    expected = np.sin(2*np.pi*0.5*1.0) * np.ones((3,1))
    assert np.allclose(s.outputs["out"], expected)


# ----------------------------------------------------------
# 4) Inconsistent parameter lengths -> error
# ----------------------------------------------------------
def test_sinusoidal_inconsistent_lengths():
    with pytest.raises(ValueError):
        Sinusoidal("s",
                   amplitude=[1.0, 2.0],
                   frequency=[1.0],  # incompatible broadcast
                   offset=[0.0, 0.0, 0.0],
                   phase=[0.0, 0.0])


# ----------------------------------------------------------
# 5) Illegal shapes
# ----------------------------------------------------------
def test_sinusoidal_illegal_matrix():
    with pytest.raises(ValueError):
        Sinusoidal("s",
                   amplitude=np.zeros((2,2)),  # forbidden
                   frequency=1.0,
                   offset=0.0,
                   phase=0.0)
