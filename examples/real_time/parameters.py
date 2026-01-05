import numpy as np

ctr_data = np.load("controller_order5_linear.npz")
K = ctr_data["feedback_gain"]
G = ctr_data["feedforward_gain"]

obs_data = np.load("observer_order5_linear.npz")
L = obs_data["observer_gain"]
A = obs_data["state_matrix"]
B = obs_data["input_matrix"]
C = obs_data["output_matrix"]
