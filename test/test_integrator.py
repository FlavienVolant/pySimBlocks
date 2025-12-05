import numpy as np

from pySimBlocks import Model, Simulator
from pySimBlocks.blocks import Sinusoidal, DiscreteIntegrator


dt = 0.01
T = 5.0
w = 1.0  # sinusoidal frequency rad/s


def compute_reference_forward(u, dt):
    """
    Forward Euler reference:
        x[k+1] = x[k] + dt * u[k]
        y[k]   = x[k]
    """
    N = len(u)
    x = np.zeros((N, 1))
    for k in range(N - 1):
        x[k+1] = x[k] + dt * u[k]
    return x


def compute_reference_backward(u, dt):
    """
    Backward Euler reference:
        y[k]   = x[k] + dt*u[k]
        x[k+1] = y[k]
    """
    N = len(u)
    x = np.zeros((N, 1))
    y = np.zeros((N, 1))
    for k in range(N):
        y[k] = x[k] + dt * u[k]
        if k < N - 1:
            x[k+1] = y[k]
    return y


def run_integrator_test(method):
    # Input: sin(w t)
    src = Sinusoidal(
        "u",
        amplitude=1.0,
        frequency=w / (2 * np.pi),
        phase=0.0,
        offset=0.0
    )

    integ = DiscreteIntegrator("int", initial_state=np.array([[0.0]]), method=method)

    model = Model("test")
    model.add_block(src)
    model.add_block(integ)
    model.connect("u", "out", "int", "in")

    sim = Simulator(model, dt=dt)
    logs = sim.run(T=T, variables_to_log=["u.outputs.out", "int.outputs.out"])

    u = np.array(logs["u.outputs.out"]).reshape(-1, 1)
    y = np.array(logs["int.outputs.out"]).reshape(-1, 1)

    # Compute discrete reference
    if method == "euler forward":
        y_ref = compute_reference_forward(u, dt)
    elif method == "euler backward":
        y_ref = compute_reference_backward(u, dt)
    else:
        raise ValueError("Unknown method")

    # Compute error
    err = np.linalg.norm(y - y_ref)

    print(f"{method} error = {err}")

    # A threshold depending on dt and numerical error
    assert err < 1e-12, f"{method} integrator mismatch!"


def test_forward():
    run_integrator_test("euler forward")


def test_backward():
    run_integrator_test("euler backward")


if __name__ == "__main__":
    test_forward()
    test_backward()
    print("All integrator tests passed.")
