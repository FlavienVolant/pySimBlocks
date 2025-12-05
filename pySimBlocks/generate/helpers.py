import os
import yaml

def python_array(x):
    """Convert list → np.array code."""
    return f"np.array({repr(x)})"

def to_camel(name):
    """Convert step → Step, linear_state_space → LinearStateSpace."""
    return "".join(w.capitalize() for w in name.split("_"))

def load_block_index():
    path = os.path.join(os.path.dirname(__file__), "pySim_blocks_index.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)

BLOCK_INDEX = load_block_index()

def resolve_class(from_group, type_name):
    class_name = to_camel(type_name)

    if from_group not in BLOCK_INDEX:
        raise ValueError(
            f"Unknown block group '{from_group}'. "
            f"Available groups: {list(BLOCK_INDEX.keys())}. "
            f"Run pysimblocks-update to refresh the metadata."
        )

    if class_name not in BLOCK_INDEX[from_group]:
        raise ValueError(
            f"Block '{class_name}' not found in group '{from_group}'. "
            f"Available blocks: {BLOCK_INDEX[from_group]}. "
            f"Run pysimblocks-update after adding new blocks."
        )

    module = f"pySimBlocks.blocks.{from_group}"

    return module, class_name
