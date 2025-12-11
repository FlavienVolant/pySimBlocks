
def python_array(x):
    """Convert list → np.array code."""
    return f"np.array({repr(x)})"


def generate_parameters(blocks, simulation):
    """
    Generate the parameters_auto.py file content.

    Parameters
    ----------
    blocks : list[dict]
    simulation : dict

    Returns
    -------
    list[str]  (file content)
    """

    lines = ["import numpy as np\n"]

    # ------------------------------------------------------------
    # 1. Block parameters
    # ------------------------------------------------------------
    for blk in blocks:
        name = blk["name"]

        for key, value in blk.items():
            if key in ["name", "type", "from"]:
                continue

            varname = f"{name}_{key}"

            # Lists become numpy arrays
            if isinstance(value, list):
                lines.append(f"{varname} = {python_array(value)}")
            else:
                lines.append(f"{varname} = {repr(value)}")

        lines.append("")  # blank line between blocks

    # ------------------------------------------------------------
    # 2. Simulation parameters
    # ------------------------------------------------------------
    dt = simulation.get("dt")
    T = simulation.get("T")

    lines.append(f"dt = {dt}")
    lines.append(f"T = {T}")

    return lines
