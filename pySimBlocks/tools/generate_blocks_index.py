import os
import yaml
import inspect
import importlib
from pySimBlocks.core.block import Block


def generate_blocks_index(output_path="pySim_blocks_index.yaml"):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blocks")
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generate", output_path)

    index = {}

    # Loop over categories: sources/, operators/, systems/, etc.
    for group in os.listdir(base_dir):
        group_path = os.path.join(base_dir, group)
        if not os.path.isdir(group_path) or group == "__pycache__":
            continue

        index[group] = []

        # Scan .py files
        for file in os.listdir(group_path):
            if not file.endswith(".py") or file == "__init__.py":
                continue

            type_name = file.replace(".py", "")
            module_path = f"pySimBlocks.blocks.{group}.{type_name}"

            try:
                module = importlib.import_module(module_path)
            except Exception:
                continue

            # Find class inheriting from Block
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module_path:
                    continue

                if Block in inspect.getmro(obj)[1:]:
                    index[group].append(name)

    # Write YAML
    with open(output_path, "w") as f:
        yaml.dump(index, f, sort_keys=True)

    print(f"[OK] Block index written to {output_path}")
    return index


if __name__ == "__main__":
    generate_blocks_index()
