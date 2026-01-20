from pySimBlocks.gui.model.block_instance import BlockInstance

class ConnectionInstance:
    def __init__(
        self,
        src_block: BlockInstance,
        src_port: str,
        dst_block: BlockInstance,
        dst_port: str,
    ):
        self.src_block = src_block
        self.src_port = src_port
        self.dst_block = dst_block
        self.dst_port = dst_port
