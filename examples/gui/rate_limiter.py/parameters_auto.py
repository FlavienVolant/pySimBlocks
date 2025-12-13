import numpy as np

ramp_slope = np.array([[10.0]])
ramp_start_time = 10
ramp_offset = np.array([[10.0]])

rate_limiter_rising_slope = 1.0
rate_limiter_falling_slope = -1
rate_limiter_initial_output = np.array([[0.0]])

dt = 0.1
T = 2.0