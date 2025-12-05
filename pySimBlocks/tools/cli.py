"""
CLI tools for pySimBlocks maintenance.

Usage:
    pysimblocks-update
"""

from pySimBlocks.tools.generate_blocks_metadata import generate_blocks_metadata


def main():
    print("Running pySimBlocks metadata update...")
    generate_blocks_metadata()
    print("pySimBlocks update complete.")
