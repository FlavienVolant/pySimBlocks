import numpy as np
import matplotlib.pyplot as plt
from pySimBlocks import Model, Simulator
from pySimBlocks.blocks.sources import Step
from pySimBlocks.blocks.systems import LinearStateSpace
from pySimBlocks.blocks.operators import Sum, Gain, DiscreteIntegrator, DiscreteDerivator
from pySimBlocks.blocks.controllers import Pid


def manual_sim(A, B, C, Kp, Ki, Kd, T, dt):
    ref = Step("ref", start_time=1., value_before=0., value_after=1.)
    motor = LinearStateSpace("motor", A, B, C)
    error = Sum("error", signs=[+1, -1])
    kp = Gain("Kp", Kp)
    ki = Gain("Ki", Ki)
    integrator = DiscreteIntegrator("integrator", method="euler backward")
    kd = Gain("Kd", Kd)
    derivator = DiscreteDerivator("derivator")
    sum = Sum("sum", num_inputs=3, signs=[+1, +1, +1])

    blocks = [ref, error, kp, integrator, ki, sum, motor, kd, derivator]

    model = Model("DC Motor Control")
    for block in blocks:
        model.add_block(block)
    model.connect("ref", "out", "error", "in1")
    model.connect("motor", "y", "error", "in2")
    model.connect("error", "out", "Kp", "in")
    model.connect("error", "out", "Ki", "in")
    model.connect("error", "out", "Kd", "in")
    model.connect("Kp", "out", "sum", "in1")
    model.connect("Ki", "out", "integrator", "in")
    model.connect("integrator", "out", "sum", "in3")
    model.connect("Kd", "out", "derivator", "in")
    model.connect("derivator", "out", "sum", "in2")
    model.connect("sum", "out", "motor", "u")

    # Simulator
    sim = Simulator(model, dt, verbose=True)
    sim.initialize()


def main():
    # DC Motor parameters
    R = 0.1
    L = 0.5
    J = 0.01
    K = 0.1
    a = 0.001

    Kp = np.array([[.001]])
    Ki = np.array([[.02]])
    Kd = np.array([[.01]])

    # Simulation parameters
    dt = 0.1
    T = 30.

    # State-space matrices
    A = np.array([[1-dt*R/L, -dt*K/L], [dt*K/J, 1-dt*a/J]])
    B = np.array([[dt/L], [0]])
    C = np.array([[0, 1]])

    manual_sim(A, B, C, Kp, Ki, Kd, T, dt)


if __name__ == "__main__":
    main()
