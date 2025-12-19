from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction

from pySimBlocks.gui_qt.model.project_state import ProjectState
from pySimBlocks.gui_qt.dialogs.simulation_settings import SimulationSettingsDialog



class ToolBarView(QToolBar):

    def __init__(self, project: ProjectState):
        super().__init__()

        self.project_state = project

        save_action = QAction("Save", self)
        save_action.triggered.connect(lambda: print("Save project"))
        self.addAction(save_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(lambda: print("Export project"))
        self.addAction(export_action)

        export_action = QAction("Display files", self)
        export_action.triggered.connect(self.open_files)
        self.addAction(export_action)

        sim_settings_action = QAction("Simulation Settings", self)
        sim_settings_action.triggered.connect(self.open_simulation_settings)
        self.addAction(sim_settings_action)

        run_action = QAction("Run", self)
        run_action.triggered.connect(lambda: print("Run simulation"))
        self.addAction(run_action)

    def open_simulation_settings(self):
        dialog = SimulationSettingsDialog(self.project_state)
        dialog.exec()

    def open_files(self):
        pass

def build_parameters_yaml(project: ProjectState) -> dict:
    data = {
        "simulation": project.simulation,
        "blocks": {},
        "logging": [],
        "plots": [],
    }

    for b in project.blocks:
        params = {
            k: v for k, v in b.parameters.items()
            if v is not None
        }
        data["blocks"][b.name] = params

    return data
def build_model_yaml(project: ProjectState) -> dict:
    return {
        "blocks": [
            {
                "name": b.name,
                "from": b.meta.category,
                "type": b.meta.type,
            }
            for b in project.blocks
        ],
        "connections": [
             [f"{c.src_block.name}.{c.src_port}",
              f"{c.dst_block.name}.{c.dst_port}",
            ]
            for c in project.connections
        ],
    }
