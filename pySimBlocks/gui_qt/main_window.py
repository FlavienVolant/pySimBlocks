from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QToolBar,
    QHBoxLayout,
)
from PySide6.QtGui import QAction

from pySimBlocks.tools.blocks_registry import load_block_registry

from pySimBlocks.gui_qt.dialogs.simulation_settings import SimulationSettingsDialog
from pySimBlocks.gui_qt.widgets.block_list import BlockList
from pySimBlocks.gui_qt.widgets.diagram_view import DiagramView
from pySimBlocks.gui_qt.model.project_state import ProjectState



registry = load_block_registry()
categories = sorted(registry.keys())



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pySimBlocks — Qt prototype")

        central = QWidget()
        layout = QHBoxLayout(central)
        self.project = ProjectState()

        self.blocks = BlockList(self.get_categories, self.get_blocks)
        self.diagram = DiagramView(self.resolve_block_meta, self.project)

        self.blocks.setFixedWidth(220)

        layout.addWidget(self.blocks)
        layout.addWidget(self.diagram)


        self.simulation_config = {
            "dt": 0.01,
            "solver": "fixed",
            "external_file": "",
        }

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        run_action = QAction("Run", self)
        run_action.triggered.connect(lambda: print("Run simulation"))
        toolbar.addAction(run_action)

        sim_settings_action = QAction("Simulation Settings", self)
        sim_settings_action.triggered.connect(self.open_simulation_settings)
        toolbar.addAction(sim_settings_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(lambda: print("Export project"))
        toolbar.addAction(export_action)

        self.setCentralWidget(central)


    def open_simulation_settings(self):
        dialog = SimulationSettingsDialog(self.simulation_config, self)
        dialog.exec()


    ####################### Registry ########################
    def get_categories(self):
        return categories.copy()

    def get_blocks(self, category):
        return sorted(registry[category].keys())

    def resolve_category_meta(self, category):
        return registry[category]

    def resolve_block_meta(self, category, block_type):
        return registry[category][block_type]
