import time

import numpy as np
import parameters as prm

from pySimBlocks.core import Model, Simulator
from pySimBlocks.project.load_project_config import load_simulation_config
from pySimBlocks.real_time import RealTimeRunner

from motors import setup_motors, send_motors_command


# ------------------------------------------------------------------------------
# Process
# ------------------------------------------------------------------------------
def process_block_diagram(shared_markers_pos, shared_ref_ol, shared_ref_cl, 
                          shared_control_mode, shared_update, 
                          event_frame, event_measure):
    """pySimblocks runner process.
    """
    init_angles = np.array([0.7, 0, 0.7, 0])
    motors = setup_motors(init_angles)

    # init pySimBlocks runner
    runner = setup_block_diagram()

    # Initialize variables
    measure = np.zeros((prm.nb_markers * 2, 1))
    ref_ol = np.zeros((2, 1))
    ref_cl = np.zeros((2, 1))
    control_mode = np.zeros((1, 1))
    command = np.zeros((2, 1))

    # Initial time for dt measurement
    t = time.perf_counter()
    dt_init = 1/60
    dt_list = []

    while True:
        event_frame.wait()
        event_frame.clear()

        send_motors_command(motors, command, init_angles)

        event_measure.wait()
        event_measure.clear()

        if dt_init is not None:
            t = time.perf_counter()
            dt = dt_init
            dt_init = None
        else:
            t2 = time.perf_counter()
            dt = t2 - t
            t = t2
        dt_list.append(dt)

        # data from camera
        with shared_markers_pos.get_lock():
            measure[:, 0] = shared_markers_pos[:]

        with shared_update.get_lock():
            if shared_update.value:
                with shared_ref_ol.get_lock():
                    ref_ol[:, 0] = shared_ref_ol[:]
                with shared_ref_cl.get_lock():
                    ref_cl[:, 0] = shared_ref_cl[:]
                with shared_control_mode.get_lock():
                    control_mode[0,0] = shared_control_mode.value
                shared_update.value = False

        outs = runner.tick(
            inputs={
                "Camera": measure,
                "Ref_ol": ref_ol,
                "Ref_cl": ref_cl,
                "Mode": control_mode
            },
            dt=dt,
            pace=False
        )
        command = outs["Cmd"]


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def setup_block_diagram():
    sim_cfg, model_cfg = load_simulation_config("parameters.yaml")
    model = Model( name="model", model_yaml="model.yaml", model_cfg=model_cfg)
    sim = Simulator(model, sim_cfg)
    runner = RealTimeRunner(
        sim,
        input_blocks=["Camera", "Ref_cl", "Ref_ol", "Mode"],
        output_blocks=["Cmd"],
        target_dt=1/60
    )
    runner.initialize()
    return runner

# -------------------------------------------------------
def select_cmd(t, dt, u_cl, u_ol, mode):
    try:
        mode = mode.item()
    except Exception:
        return {"u": np.zeros((2,1))}

    if mode == 0:
        return {"u": u_ol}
    elif mode == 1:
        return {"u": u_cl}
    else:
        return {"u": np.zeros((2,1))}


# -------------------------------------------------------
def filter_first_order(t, dt, u, u_prev):
    """Apply a first-order low-pass filter to the signal."""
    if dt <= 0:
        return {"u_filter" : np.zeros((2,1))}
    cutoffFreq = 30.  # Cutoff frequency in Hz
    samplingFreq = 1 / dt

    timeConstant = 1 / (2 * np.pi * cutoffFreq)
    samplingPeriod = 1 / samplingFreq
    alpha = samplingPeriod / (timeConstant + samplingPeriod)
    uf = alpha * u + (1 - alpha) * u_prev

    return {"u_filter" : uf}


if __name__ == "__main__":
    setup_block_diagram() 
