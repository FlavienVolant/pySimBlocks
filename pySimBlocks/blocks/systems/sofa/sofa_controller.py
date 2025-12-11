from pySimBlocks import Simulator
import Sofa

class SofaPysimBlocksController(Sofa.Core.Controller):
    """
    Base class for controller to enable Sofa Simulation Loop and pySimBlocks to interact.

    Description:
        - SOFA_MASTER: SOFA is the time master.
                        At each animation step, the controller:
                            1) reads measurements from the scene
                            2) performs one pySimBlocks step
                            3) applies the computed control inputs

        - Non-SOFA_MASTER: pySimBlocks is the time master.
                            The controller is used ONLY as an I/O shell.
                            No pySimBlocks model is built or executed.

    Required methods:
        - set_inputs(self)
        - get_outputs(self)

    Optional methods:
        - build_model()  : create self.model, self.sofa_block and variables_to_log
        - print_logs()  : print logs at each step (already implemented)
        - save()

    optional parameter:
        - variables_to_log: list of signal to log
    """

    SOFA_MASTER = True

    def __init__(self, name="SofaControllerGui"):
        super().__init__(name=name)

        # MUST be filled by child controllers
        self.inputs  = {}
        self.outputs = {}
        self.variables_to_log = []
        self.verbose = False

        self.sim = None

    # ----------------------------------------------------------------------
    # Mandatory          ---------------------------------------------------
    # ----------------------------------------------------------------------
    def set_inputs(self):
        """
        Apply inputs from pySimBlocks to SOFA components.
        Must be implemented by child classes.
        """
        raise NotImplementedError("set_inputs() must be implemented by subclass.")

    def get_outputs(self):
        """
        Read state from SOFA components and populate self.outputs.
        Must be implemented by child classes.
        """
        raise NotImplementedError("get_outputs() must be implemented by subclass.")

    # ----------------------------------------------------------------------
    # Not mandatory but still need to be defined by the user. --------------
    # ----------------------------------------------------------------------
    def build_model(self):
        """
        Define the internal pySimBlocks controller model.

        Must create:
            - self.model
            - the exchange block self.sofa_block (SofaExchangeIO)
            - self.variables_to_log
        """
        raise NotImplementedError("build_model() must be implemented by subclass.")

    def save(self):
        """
        Optional: save logged data at the end of the simulation.
        To be implented with saving condition.
        """
        raise NotImplementedError("save() must be implemented by subclass.")
    # ----------------------------------------------------------------------
    # Specific functions ---------------------------------------------------
    # ----------------------------------------------------------------------
    def initialize_pysimblocks(self):
        """Called once SOFA is initialized AND if SOFA is the master."""
        self.build_model()
        self.setup_sim(self.root.dt.value)


    def setup_sim(self, dt):
        """
        Initialize the internal pySimBlocks simulator.

        Parameters
        ----------
        dt : float
            Simulation time step (must match SOFA's dt).
        verbose : bool
            Enable or disable controller logging.
        """
        self.sim = Simulator(self.model, dt=dt, verbose=self.verbose)
        self.sim.initialize()
        self.step_index = 0

    # non mandatory
    def print_logs(self):
        """
        Optional: print selected logged variables at each control step.
        Already implemented
        """
        print(f"\nStep: {self.step_index}")
        for variable in self.variables_to_log:
            print(f"{variable}: {self.sim.logs[variable][-1]}")

    # ----------------------------------------------------------------------
    # SOFA event callback ---------------------------------------------------
    # ----------------------------------------------------------------------
    def onAnimateBeginEvent(self, event):
        """
        SOFA callback executed before each physical integration step.

        Sequence:
            1. Read SOFA outputs  → get_outputs()
            2. Push them into the exchange block
            3. Advance pySimBlocks one step → sim.step()
            4. Retrieve controller inputs from exchange block
            5. Apply them to SOFA → set_inputs()
        """
        if self.SOFA_MASTER:
            if self.sim is None:
                self.initialize_pysimblocks()

            self.get_outputs()
            for keys, val in self.outputs.items():
                self.sofa_block.outputs[keys] = val

            self.sim.step()
            self.sim._log(self.variables_to_log)

            for key, val in self.sofa_block.inputs.items():
                self.inputs[key] = val
            self.set_inputs()

            if self.verbose:
                self.print_logs()

            self.save()
            self.step_index += 1
