# Non Linear State Space

## Summary

The **NonLinearStateSpace** block evaluates a user-defined, discrete-time non linear state space system without direct feedthrough.

---

## Mathematical definition

The block implements a general algebraic relation of the form:

$$
x[k+1] = g(t_k, \Delta t_k, x[k] u_1[k], u_2[k], \dots)
$$

$$
y[k] = g(t_k, \Delta t_k, x[k])
$$

where:
- $x[k]$ is the state vector
- $u_i[k]$ are the input signals,
- $y[k]$ is the output signal,
- $t_k$ is the current simulation time,
- $\Delta t_k$ is the time step since the previous activation.

The functions $f$ and $g$ are provided by the user as a Python function.

---

## Parameters

### `file_path` (required)

Path to the Python file containing the user-defined function.

- Must point to a valid Python file
- Path resolution is handled externally by the project loader

### `state_function_name` (required)

Name of the state function to call inside the Python file.

### `output_function_name` (required)

Name of the output function to call inside the Python file.

### `input_keys` (required)

List of input port names.

- Defines the block input ports
- Must match the function arguments after `(t, dt)`

### `output_keys` (required)

List of output port names.

- Defines the block output ports
- The function must return a dictionary with exactly these keys

### `sample_time` (optional)

Execution period of the block.

If not specified, the simulator time step is used.

---

## Inputs

Inputs are dynamically defined by `input_keys`.

- Each input must be connected
- Dimension: $(n, 1)$

## Outputs

Outputs are dynamically defined by `output_keys`.

- Each output is computed at each simulation step
- Dimension: $(n, 1)$

---

## Execution semantics

- The block has a state.
- The block has no feedthrough.
- At each activation, the function is evaluated as:

```python
f(t, dt, x, **inputs)
g(t, dt, x)
```
