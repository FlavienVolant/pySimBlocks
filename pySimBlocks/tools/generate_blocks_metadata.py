from pySimBlocks.tools.generate_blocks_registry import generate_registry
from pySimBlocks.tools.generate_blocks_index import generate_blocks_index


def generate_blocks_metadata():
    print("=== Generating pySimBlocks metadata ===")

    # Generate index (class names only)
    generate_blocks_index()

    # Generate registry (full metadata)
    generate_registry()



    print("=== Metadata generation complete ===")


if __name__ == "__main__":
    generate_blocks_metadata()
