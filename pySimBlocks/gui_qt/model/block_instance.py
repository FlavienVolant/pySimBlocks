class BlockInstance:
    """
    GUI-side mutable instance of a block.

    - References an immutable BlockMeta
    - Stores instance-level data (name, parameters)
    - Used by BlockItem and BlockDialog
    """

    def __init__(self, meta):
        self.meta = meta
        self.name = meta.name
        self.parameters = self._init_parameters()

    def _init_parameters(self) -> dict:
        """
        Initialize instance parameters from metadata.
        """
        params = {}

        for pname, pmeta in self.meta.parameters.items():
            if pmeta.get("autofill", False):
                params[pname] = pmeta.get("default")
            else:
                params[pname] = None

        return params
