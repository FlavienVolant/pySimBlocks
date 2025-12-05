from multiprocessing import Process, Pipe
import numpy as np

def sofa_worker(conn):
    import Sofa
    from Finger import createScene

    root = Sofa.Core.Node("root")
    root, controller = createScene(root)
    Sofa.Simulation.initRoot(root)
    dt = root.dt.value
    Sofa.Simulation.animate(root, dt)  # Initial animate to setup

    positions = []

    for i in range(500):
        positions.append(controller.outputs["tip"].copy())
        controller.inputs["cable"] = 1 if i > 50 else 0
        Sofa.Simulation.animate(root, dt)

    conn.send(np.array(positions))
    conn.close()


def main():
    parent_conn, child_conn = Pipe()
    p = Process(target=sofa_worker, args=(child_conn,))
    p.start()
    positions = parent_conn.recv()
    p.join()

    print("Simulation finished, shape:", positions.shape)

    # Plot without crash
    import matplotlib.pyplot as plt
    t = np.arange(len(positions)) * 0.01
    plt.plot(t, positions[:, 0], label="X")
    plt.plot(t, positions[:, 1], label="Y")
    plt.plot(t, positions[:, 2], label="Z")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
