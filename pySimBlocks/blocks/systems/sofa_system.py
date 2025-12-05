import os
import importlib.util
import numpy as np
import Sofa
from pySimBlocks.core.block import Block


class SofaSystem(Block):
    """
    Sofa co-simulation block.

    Description:
        Loads a Sofa scene defined in an external Python file.
        The scene must expose a `createScene(root) -> (rootNode, controller)`
        where `controller` is a Sofa Controller exposing:

            controller.inputs  : dict input_name -> value (np arrays or floats)
            controller.outputs : dict output_name -> value (np arrays or floats)

        Required behaviour of the controller:
        - onAnimateBeginEvent:
             * Reads all controller.inputs[...] provided by pySim
             * Applies them to the internal Sofa model
             * Computes controller.outputs[...] from internal state

    Parameters:
        name: str
            Block name.
        scene_file: str
            Path to the Python file containing createScene().
        input_keys: list[str]
            Input port names expected by the controller.
        output_keys: list[str]
            Output port names produced by the controller.
    """

    def __init__(self, name: str, scene_file: str,
                 input_keys: list[str], output_keys: list[str]):

        super().__init__(name)

        self.scene_file = scene_file
        self.input_keys = list(input_keys)
        self.output_keys = list(output_keys)

        # PySim ports
        for key in self.input_keys:
            self.inputs[key] = None

        for key in self.output_keys:
            self.outputs[key] = None

        # Internal Sofa references
        self.root = None
        self.controller = None
        self.dt = None


    # ------------------------------------------------------
    # LOAD SCENE MODULE
    # ------------------------------------------------------
    def _import_scene(self):
        """Dynamically import scene file."""
        path = os.path.abspath(self.scene_file)
        module_name = os.path.splitext(os.path.basename(path))[0]

        spec = importlib.util.spec_from_file_location(module_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        if not hasattr(mod, "createScene"):
            raise RuntimeError(f"Scene file {path} has no createScene() function.")

        return mod.createScene


    # ------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------
    def initialize(self, t0: float):

        createScene = self._import_scene()

        # Create an empty root
        root = Sofa.Core.Node("root")
        root, controller = createScene(root)

        if controller is None:
            raise RuntimeError("createScene() must return (root, controller).")

        self.root = root
        self.controller = controller

        # Extract dt from scene
        try:
            self.dt = float(root.dt.value)
        except:
            raise RuntimeError("Scene must define root.dt.value.")

        # Initialize sofa graph
        Sofa.Simulation.initRoot(root)

        # Initialize controller inputs DYNAMICALLY
        # Do NOT assign default values, preserve whatever the controller defined.
        for key in self.input_keys:
            if key not in self.controller.inputs:
                self.controller.inputs[key] = None

        # Initialize outputs
        for key in self.output_keys:
            self.outputs[key] = None

        # First animate to compute initial outputs
        Sofa.Simulation.animate(root, self.dt)

        # Capture initial outputs
        for key in self.output_keys:
            val = self.controller.outputs.get(key, None)
            if val is None:
                raise RuntimeError(
                    f"Controller did not set output '{key}' during initialization."
                )
            self.outputs[key] = np.asarray(val).reshape(-1, 1)



    # ------------------------------------------------------
    # PHASE 1 : output_update
    # ------------------------------------------------------
    def output_update(self, t: float):
        """Outputs were computed by previous animate()."""
        for key in self.output_keys:
            val = self.controller.outputs.get(key, None)
            if val is None:
                raise RuntimeError(f"Missing output '{key}' at t={t}.")
            self.outputs[key] = np.asarray(val).reshape(-1, 1)


    # ------------------------------------------------------
    # PHASE 2 : state_update
    # ------------------------------------------------------
    def state_update(self, t: float, dt: float):
        """Send inputs to Sofa and execute one animation step."""

        # 1. Pass inputs AS THEY ARE
        for key in self.input_keys:
            val = self.inputs[key]
            if val is None:
                raise RuntimeError(f"Input '{key}' not set at t={t}.")

            # Direct transmission
            # No reshape, no float conversion, no assumptions.
            self.controller.inputs[key] = val

        # 2. Trigger Sofa step
        Sofa.Simulation.animate(self.root, self.dt)
