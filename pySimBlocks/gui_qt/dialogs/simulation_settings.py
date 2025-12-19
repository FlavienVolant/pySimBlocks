from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
)

from pySimBlocks.gui_qt.model.project_state import ProjectState

class SimulationSettingsDialog(QDialog):
    def __init__(self, project:ProjectState, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Settings")
        self.setMinimumWidth(350)

        self.project_state = project

        main_layout = QVBoxLayout(self)
        self.build_form(main_layout)
        self.build_buttons(main_layout)


    def build_form(self, layout):
        form = QFormLayout()
        title = QLabel("<b>Simulation Settings</b>")
        form.addRow(title)
        dt = self.project_state.simulation.get("dt", 0.01)
        self.dt_edit = QLineEdit(str(dt))
        form.addRow(QLabel("Step time:"), self.dt_edit)

        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["fixed", "variable"])
        self.solver_combo.setCurrentText(self.project_state.simulation.get("solver", "fixed"))
        form.addRow("Solver:", self.solver_combo)

        T = self.project_state.simulation.get("T", 10.)
        self.T_edit = QLineEdit(str(T))
        form.addRow(QLabel("Stop time:"), self.T_edit)

        external = self.project_state.external
        external = "" if external is None else external
        self.file_edit = QLineEdit(external)
        form.addRow(QLabel("Python File:"), self.file_edit)

        layout.addLayout(form)


    # ------------------------------------------------------------
    # Buttons
    def build_buttons(self, layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        ok_btn = QPushButton("Ok")
        ok_btn.setDefault(True)
        ok_btn.setAutoDefault(True)
        ok_btn.clicked.connect(self.ok)
        buttons_layout.addWidget(ok_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply)
        buttons_layout.addWidget(apply_btn)

        layout.addLayout(buttons_layout)

    def apply(self):
        self.project_state.simulation["dt"] = self.dt_edit.text()
        self.project_state.simulation["solver"] = self.solver_combo.currentText()

        file = self.file_edit.text()
        self.project_state.external = None if file == "" else file
        self.accept()

    def ok(self):
        self.apply()
        self.reject()
