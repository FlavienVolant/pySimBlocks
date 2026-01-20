from typing import Any, Dict, Literal

class PortInstance:
    def __init__(
        self,
        name: str,
        direction: Literal['input', 'output'],
        block, # BlockInstance, can't import type due to circular import
        meta: Dict[str, Any],
    ):
        self.name = name
        self.direction = direction
        self.block = block
        self.meta = meta
