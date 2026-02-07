import time

import numpy as np
from emioapi import EmioMotors


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
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

# -------------------------------------------------------
def send_motors_command(motors, command, init_angles=np.array([0, 0, 0, 0])):
    command = command.flatten()
    motors.angles = [command[0] + init_angles[0], init_angles[1],
                     command[1] + init_angles[2], init_angles[3]]

# -------------------------------------------------------
def get_motors_position(motors, init_angles=np.array([0, 0, 0, 0])):
    motors_pos = np.array(motors.angles) - init_angles
    return motors_pos[[0, 2]].reshape((2, 1))
