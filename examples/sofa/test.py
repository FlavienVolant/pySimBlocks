import os
import numpy
import matplotlib.pyplot as plt

from pySimBlocks import Model, Simulator
from pySimBlocks.blocks.systems import SofaSystem
from pySimBlocks.blocks.sources import Step


def main():

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Finger.py')


    # --- Create Blocks ---
    step = Step(
        name="step",
        value_before=0.0,
        value_after=1.0,
        t_step=0.5,
    )

    sofa_block = SofaSystem(
        name="sofa_finger",
        scene_file=path,
        input_keys=["cable"],
        output_keys=["tip"],
    )

    # --- Build the model ---
    model = Model(name="sofa_finger_model")
    model.add_block(step)
    model.add_block(sofa_block)
    model.connect("step", "out", "sofa_finger", "cable")


    # --- Create the simulator ---
    dt = 0.01
    sim = Simulator(model, dt=dt)

    # --- Run simulation ---
    T = 5.0
    logs = sim.run(
        T=T,
        variables_to_log=[
            "step.outputs.out",
            "sofa_finger.outputs.tip",
        ],
    )

    # --- Inspect / print some results ---
    t = numpy.arange(0, T, dt)
    length = min(len(t), len(logs["sofa_finger.outputs.tip"]))
    t = t[:length]
    u = numpy.array(logs["step.outputs.out"]).reshape(length, -1)
    tip_positions = numpy.array(logs["sofa_finger.outputs.tip"]).reshape(length, -1)

    print("Recorded tip positions:", tip_positions.shape)

    plt.figure()
    for i in range(3):
        plt.plot(t, tip_positions[:, i], label=f"Axis {i}")
    plt.legend()
    plt.grid(True)
    plt.xlabel("Time [s]")
    plt.ylabel("Tip Position")
    plt.title("Finger Tip Position Over Time")
    plt.show()


if __name__ == '__main__':
    main()
