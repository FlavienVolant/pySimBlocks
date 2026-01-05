# External Input Block

## Description

The External Input block represents a data input point in a simulation model. It allows external signals to be fed into the model during simulation. The block outputs the value of the external signal at each simulation time step.

---

## Parameters

| Name        | Description |
|------------|-------------|
| `sample_time` | Optional block sample time. If omitted, the global simulation time step is used. |

---

## Inputs

| Port | Description |
|------|------------|
| `in` | External data signal \( u \). |

---

## Outputs

| Port | Description |
|------|------------|
| `out` | Model data signal. |

---

## Notes

- The External Input block is **stateless**.
