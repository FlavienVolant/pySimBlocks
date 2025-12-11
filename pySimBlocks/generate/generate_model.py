import os
import yaml


# =============================================================================
# Load block index
# =============================================================================

def _load_block_index():
    index_path = os.path.join(os.path.dirname(__file__), "pySimBlocks_blocks_index.yaml")
    with open(index_path, "r") as f:
        return yaml.safe_load(f)

BLOCK_INDEX = _load_block_index()


def resolve_block_import(group: str, block_type: str):
    """Return (module, class_name) from the block index."""
    try:
        entry = BLOCK_INDEX[group][block_type]
    except KeyError:
        raise KeyError(f"[resolve_block_import] Unknown block '{block_type}' in group '{group}'.")
    return entry["module"], entry["class"]


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_model(blocks, connections):
    """
    Generate the model.py content.
    """

    lines = []
    imports = set()

    # -------------------------------------------------------------------------
    # Imports
    # -------------------------------------------------------------------------
    imports.add("from pySimBlocks import Model, Simulator")
    imports.add("from parameters_auto import *")

    for blk in blocks:
        group = blk["from"]
        block_type = blk["type"]
        module, class_name = resolve_block_import(group, block_type)
        imports.add(f"from {module} import {class_name}")

    # Format imports
    lines.extend(sorted(imports))
    lines.append("")

    # -------------------------------------------------------------------------
    # Instantiate model
    # -------------------------------------------------------------------------
    lines.append("model = Model('auto_model')\n")

    # -------------------------------------------------------------------------
    # Instantiate blocks
    # -------------------------------------------------------------------------
    for blk in blocks:
        name = blk["name"]
        group = blk["from"]
        block_type = blk["type"]

        module, class_name = resolve_block_import(group, block_type)

        # Load params from parameters_auto
        params = {k: f"{name}_{k}" for k in blk if k not in ("name", "from", "type")}

        if params:
            params_str = ", ".join(f"{k}={v}" for k, v in params.items())
            lines.append(f"{name} = {class_name}('{name}', {params_str})")
        else:
            lines.append(f"{name} = {class_name}('{name}')")

        lines.append(f"model.add_block({name})\n")

    # -------------------------------------------------------------------------
    # Connections
    # -------------------------------------------------------------------------
    for conn in connections:
        src_full, dst_full = conn
        src, outp = src_full.split(".")
        dst, inp = dst_full.split(".")
        lines.append(f"model.connect('{src}', '{outp}', '{dst}', '{inp}')")

    lines.append("")

    lines.append("simulator = Simulator(model, dt=dt)")

    return lines
