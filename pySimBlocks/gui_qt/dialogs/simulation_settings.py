from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
    QFileDialog
)

class SimulationSettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Settings")
        self.setMinimumWidth(350)

        self.config = config  # shared dict (V1 simple)

        main_layout = QVBoxLayout(self)

        form = QFormLayout()

        # --- dt ---
        self.dt_edit = QLineEdit(str(config.get("dt", 0.01)))
        form.addRow("Time step (dt):", self.dt_edit)

        # --- solver ---
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["fixed", "variable"])
        self.solver_combo.setCurrentText(config.get("solver", "fixed"))
        form.addRow("Solver:", self.solver_combo)

        # --- external python file ---
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit(config.get("external_file", ""))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        form.addRow("External Python file:", file_layout)

        main_layout.addLayout(form)

        # --- buttons ---
        buttons = QHBoxLayout()
        buttons.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply)
        buttons.addWidget(apply_btn)

        main_layout.addLayout(buttons)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Python file", "", "Python files (*.py)"
        )
        if path:
            self.file_edit.setText(path)

    def apply(self):
        self.config["dt"] = self.dt_edit.text()
        self.config["solver"] = self.solver_combo.currentText()
        self.config["external_file"] = self.file_edit.text()

        print("Simulation settings updated:")
        print(self.config)

        self.accept()
