import numpy as np
import matplotlib.pyplot as plt

from pySimBlocks import Model, Simulator
from pySimBlocks.blocks import Sinusoidal, DiscreteDerivator


dt = 0.1
T = 2.0
w = 2.0  # rad/s


# ============================================================
# Reference discrete derivative functions
# ============================================================

def ref(u, dt):
    """
    Reference discrete derivative for n-dimensional signals.
    u is shape (N, n)
    y[k] = (u[k] - u[k-1]) / dt
    y[0] = 0
    """
    N, n = u.shape
    y = np.zeros((N, n))
    for k in range(1, N):
        y[k] = (u[k] - u[k-1]) / dt
    return y


# ============================================================
# Generic test runner
# ============================================================

def run_test(amplitude, phase, offset, case, plot=False):
    """
    Generic test function:
    - Build model: sinusoidal → derivator(method)
    """

    # Input: sinusoid u(t) = sin(w t)
    src = Sinusoidal(
        "u",
        amplitude=amplitude,
        frequency=w/(2*np.pi),
        phase=phase,
        offset=offset,
    )

    deriv = DiscreteDerivator("deriv")

    model = Model("test_deriv")
    model.add_block(src)
    model.add_block(deriv)
    model.connect("u", "out", "deriv", "in")

    sim = Simulator(model, dt=dt)
    logs = sim.run(T=T, variables_to_log=["u.outputs.out", "deriv.outputs.out"])

    length = len(logs["u.outputs.out"])
    u = np.array(logs["u.outputs.out"]).reshape(length, -1)
    y = np.array(logs["deriv.outputs.out"]).reshape(length, -1)
    t = np.arange(0, len(y)) * dt

    # Compute discrete reference
    y_ref = ref(u, dt)

    if plot:
        plt.figure()
        for i in range(y.shape[1]):
            plt.subplot(y.shape[1], 1, i+1)
            plt.plot(t, y[:, i], '-.', label="Simulated derivative")
            plt.plot(t, y_ref[:, i], '--', label="Reference derivative")
            plt.title(f"Case {case} - Component {i}")
            plt.legend()
        plt.tight_layout()
        plt.show()

    # Compute numerical error
    err = np.linalg.norm(y - y_ref)

    print(f"Case {case} - Error = {err}")
    assert err < 1e-12, f"Case {case} - Discrete derivative mismatch !"

# ============================================================
# Test cases
# ============================================================
def test_discrete_derivator_1d():
    run_test(amplitude=1.0, phase=0.0, offset=0.0, case="1D")

def test_discrete_derivator_nd():
    run_test(
        amplitude=np.array([1.0, 0.5, 2.0]),
        phase=np.array([0.0, np.pi/4, np.pi/2]),
        offset=np.array([0.0, 1.0, -1.0]),
        case="nD",
    )

# ============================================================
# Main execution
# ============================================================

if __name__ == "__main__":
    test_discrete_derivator_1d()
    test_discrete_derivator_nd()
    print("All DiscreteDerivator tests passed.")
