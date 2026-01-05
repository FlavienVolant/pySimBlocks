import os
import psutil
import time
import numpy as np
import multiprocessing
import cv2 as cv

from pySimBlocks.core import Model, Simulator
from pySimBlocks.project.load_project_config import load_simulation_config

from emioapi import EmioMotors
from emioapi._depthcamera import DepthCamera


nb_markers = 3

############################################################################
# Camera helpers
#############################################################################
def setup_camera():
    camera = DepthCamera(
        show_video_feed=True,
        tracking=True,
        compute_point_cloud=False)
    camera.set_fps(60)
    camera.set_depth_min(0)
    camera.set_depth_max(1000)
    camera.open()
    return camera

def pixel_to_mm(points, depth):
    ppx, ppy = 319.475, 240.962
    fx, fy = 382.605, 382.605
    points[:, 0] = ((points[:, 0] - ppx) / fx) * depth
    points[:, 1] = ((points[:, 1] - ppy) / fy) * depth
    points = np.column_stack((points[:, 2], -points[:, 1], points[:, 0]))
    return points.copy()

def camera_to_sofa_order(points):
    i_ymax = np.argmax(points[:, 1])
    i_rest = [i for i in range(nb_markers) if i != i_ymax]
    i_sorted_z = sorted(i_rest, key=lambda i: points[i, 2])
    new_order = [i_sorted_z[1], i_sorted_z[0], i_ymax]
    return points[new_order].flatten()

def process_frame(camera):
    camera.process_frame()
    if len(camera.trackers_pos) == nb_markers:
        pos = np.array(camera.trackers_camera).reshape(nb_markers, 3).copy() # if front camera
        pos = pixel_to_mm(pos, 249) # if front camera
        markers_pos = camera_to_sofa_order(pos)
        return markers_pos
    return np.zeros((3 * nb_markers))

############################################################################
# Motors helpers
#############################################################################
def setup_motors(init_angles=[0, 0, 0, 0]):
    motors = EmioMotors()
    while not motors.open():
        print("Waiting for motors to open...")
        time.sleep(1)
    print("Motors opened successfully.")
    motors.position_p_gain = [2000, 800, 2000, 800]
    motors.position_i_gain = [0, 0, 0, 0]
    motors.position_d_gain = [50, 0, 50, 0]
    time.sleep(1)
    motors.angles = init_angles
    return motors

def send_motors_command(motors, command):
    motors.angles = [command[0], 0, command[1], 0]

def get_motors_position(motors):
    motors_pos = np.array(motors.angles)[[0, 2]]
    return motors_pos

############################################################################
# pySimBlocks helpers
#############################################################################
def setup_blocks():
    sim_cfg, model_cfg = load_simulation_config("parameters.yaml")
    model = Model( name="model", model_yaml="model.yaml", model_cfg=model_cfg)
    sim = Simulator(model, sim_cfg)
    sim.initialize()
    return sim

############################################################################
# Process
#############################################################################
def process_camera(shared_markers_pos, event_measure, event_command):
    """Update tracker position."""
    p = psutil.Process(os.getpid())
    p.cpu_affinity([0])
    p.nice(0)
    camera = setup_camera()

    while True:
        # get frame from camera
        ret = camera.get_frame()
        event_command.set() # ask to send command

        if ret:
            pos = process_frame(camera)
            with shared_markers_pos.get_lock():
                shared_markers_pos[:] = pos

        event_measure.set() # signal that measurement is ready

        k = cv.waitKey(1)
        if k == ord('q'):
            camera.quit()
            break

def process_main(shared_markers_pos, event_measure, event_command):
    """Main control loop."""
    p = psutil.Process(os.getpid())
    p.cpu_affinity([2])
    p.nice(0)

    motors = setup_motors(init_angles=[0, 0, 0, 0])
    block_sim = setup_blocks()

    # get block_motor and block_camera
    block_ref = block_sim.model.get_block_by_name("Reference")
    block_camera = block_sim.model.get_block_by_name("Camera")
    block_motor = block_sim.model.get_block_by_name("Motor")

    # Initialize variables
    markers_pos = np.zeros((nb_markers * 3,))
    measure = np.zeros((nb_markers * 2,))
    motors_pos = np.zeros((2,))
    command = np.zeros((2,))

    t = time.time()

    while True:
        # On event, read current pos and send previous command
        event_command.wait()
        event_command.clear()
        motors_pos = get_motors_position(motors)
        send_motors_command(motors, command)

        # On event (camera ready), read markers position
        event_measure.wait()
        event_measure.clear()
        with shared_markers_pos.get_lock():
            markers_pos = np.array(shared_markers_pos[:])
        measure = markers_pos[[1, 2, 4, 5, 7, 8]]


        # Update pySimBlocks inputs
        block_ref.inputs['in'] = np.zeros((2,))
        block_camera.inputs['in'] = measure

        # Simulate one step
        block_sim.step()

        # Update pySimBlocks outputs
        command = block_motor.outputs['out'].flatten()

        t2 = time.time()
        dt = t2 - t
        t = t2
        print(f"dt main loop: {dt*1000:.2f} ms")


def main():

    # shared variables
    shared_markers_pos = multiprocessing.Array("d", 3 * nb_markers * [0.])
    shared_motors_command = multiprocessing.Array("d", 2 * [0.0])
    event_measure = multiprocessing.Event()
    event_command = multiprocessing.Event()

    # Create processes
    p1 = multiprocessing.Process(target=process_camera, args=(shared_markers_pos, event_measure, event_command))
    p2 = multiprocessing.Process(target=process_main, args=(shared_markers_pos, event_measure, event_command))

    p1.start()
    p2.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()


def createScene(root):
    """Create the scene for the direct control application."""
    main()

if __name__ == "__main__":
    main()
