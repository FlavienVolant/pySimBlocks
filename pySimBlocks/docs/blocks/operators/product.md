# Product Block

## Description

The **Product** block computes a multiplication or division of multiple input signals.

If multiplication is "Element-wise (*)", it performs element-wise multiplication or division:
$$ y = u_1 oper_1 u_2 oper_2 \dots oper_{N-1} u_N $$
where each coefficient \( oper_i \) is either * or /.

If multiplication is "Matrix (@)", it performs matrix multiplication or division:
$$ y = u_1 oper_1 u_2 oper_2 \dots oper_{N-1} u_N $$
where each coefficient \( oper_i \) is either * (matrix product @) or / (matrix inverse).

---

## Parameters

| Name | Description |
|------|------------|
| `operations` | List of * or / operations applied between each input. |
| `multiplication` | Either 'Element-wise (*)' or 'Matrix (@)' multiplication. |
| `sample_time` | Optional block sample time. |

---

## Inputs

| Port | Description |
|------|------------|
| `in1 … inN` | Input signals to be multiplied or divided. All inputs must have identical dimensions or scalar |

---

## Outputs

| Port | Description |
|------|------------|
| `out` | Result of the multiplication/division of all input signals. |

---

## Notes

- The Sum block has no internal state.
- The Sum block is direct-feedthrough.
- The number of input ports is determined by the length of `operations` + 1 .
