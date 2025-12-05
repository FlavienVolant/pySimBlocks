import os
import numpy
import matplotlib.pyplot as plt

from pySimBlocks import Model, Simulator
from pySimBlocks.blocks.systems import SofaSystem
from pySimBlocks.blocks.sources import Step
from pySimBlocks.blocks.operators import Gain, Sum, DiscreteIntegrator


def main():

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finger', 'Finger.py')


    # --- Create Blocks ---
    step = Step(
        name="step",
        value_before=[[0.0]],
        value_after=[[8.0]],
        t_step=0.4,
    )

    kp = Gain(name="kp", gain=0.5)
    ki = Gain(name="ki", gain=0.8)
    error = Sum(name="error", num_inputs=2, signs=[1, -1])
    sum = Sum(name="sum", num_inputs=2, signs=[1, 1])
    integrator = DiscreteIntegrator(name="integrator", initial_state=[[0.0]])

    sofa_block = SofaSystem(
        name="sofa_finger",
        scene_file=path,
        input_keys=["cable"],
        output_keys=["tip", "measure"],
    )

    # --- Build the model ---
    model = Model(name="sofa_finger_model")
    for block in [step, kp, ki, error, sum, integrator, sofa_block]:
        model.add_block(block)

    model.connect("step", "out", "error", "in1")
    model.connect("sofa_finger", "measure", "error", "in2")
    model.connect("error", "out", "kp", "in")
    model.connect("error", "out", "integrator", "in")
    model.connect("integrator", "out", "ki", "in")
    model.connect("kp", "out", "sum", "in1")
    model.connect("ki", "out", "sum", "in2")
    model.connect("sum", "out", "sofa_finger", "cable")


    # --- Create the simulator ---
    dt = 0.01
    sim = Simulator(model, dt=dt)

    # --- Run simulation ---
    T = 5.0
    logs = sim.run(
        T=T,
        variables_to_log=[
            "step.outputs.out",
            "sofa_finger.outputs.measure",
            "sum.outputs.out"
        ],
    )

    # --- Inspect / print some results ---
    t = numpy.arange(0, T, dt)
    length = min(len(t), len(logs["sofa_finger.outputs.measure"]))
    t = t[:length]
    r = numpy.array(logs["step.outputs.out"]).reshape(length, -1)
    u = numpy.array(logs["sum.outputs.out"]).reshape(length, -1)
    y = numpy.array(logs["sofa_finger.outputs.measure"]).reshape(length, -1)

    print("Recorded tip positions:", y.shape)

    plt.figure()
    plt.step(t, r, 'r--', label="Reference")
    plt.step(t, y[:, 0], 'b--', label=f"Measure")
    plt.legend()
    plt.grid(True)
    plt.xlabel("Time [s]")
    plt.ylabel("Tip Position")
    plt.title("Finger Tip Position Over Time")

    plt.figure()
    plt.step(t, u[:, 0], 'g--', label="Control Signal")
    plt.legend()
    plt.grid(True)
    plt.xlabel("Time [s]")
    plt.ylabel("Control Signal")
    plt.title("Control Signal Over Time")
    plt.show()


if __name__ == '__main__':
    main()
