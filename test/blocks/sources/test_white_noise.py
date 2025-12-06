import numpy as np
import pytest

from pySimBlocks.blocks.sources.white_noise import WhiteNoise


# ----------------------------------------------------------
# 1) Scalar noise, deterministic with seed
# ----------------------------------------------------------
def test_white_noise_scalar_reproducible():
    s1 = WhiteNoise("n", mean=0.0, std=1.0, seed=42)
    s2 = WhiteNoise("n", mean=0.0, std=1.0, seed=42)

    s1.initialize(0.0)
    s2.initialize(0.0)

    assert np.allclose(s1.outputs["out"], s2.outputs["out"])


def test_white_noise_scalar_update():
    s = WhiteNoise("n", mean=2.0, std=0.5, seed=0)
    s.initialize(0.0)
    first = s.outputs["out"].copy()
    s.output_update(0.1)
    second = s.outputs["out"]

    # noise must change at each update
    assert not np.allclose(first, second)


# ----------------------------------------------------------
# 2) Vector parameters + broadcasting
# ----------------------------------------------------------
def test_white_noise_vector_params():
    s = WhiteNoise("n",
                    mean=[1.0, 2.0],
                    std=[0.1, 0.2],
                    seed=10)
    s.initialize(0.0)
    out = s.outputs["out"]
    assert out.shape == (2,1)


def test_white_noise_broadcast_scalar_mean():
    s = WhiteNoise("n",
                    mean=0.0,
                    std=[1.0, 2.0, 3.0],
                    seed=1)
    s.initialize(0.0)
    assert s.mean.shape == (3,1)
    assert s.std.shape == (3,1)


# ----------------------------------------------------------
# 3) Error cases
# ----------------------------------------------------------
def test_white_noise_inconsistent_sizes():
    with pytest.raises(ValueError):
        WhiteNoise("n",
                    mean=[1.0, 2.0],
                    std=[1.0, 2.0, 3.0],  # cannot broadcast to 2
                    )


def test_white_noise_negative_std():
    with pytest.raises(ValueError):
        WhiteNoise("n", mean=0.0, std=-1.0)
