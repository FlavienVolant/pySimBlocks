from pathlib import Path
from PySide6.QtWidgets import (
    QHBoxLayout,
    QDialog,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
    QMessageBox,
    QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt

from pySimBlocks.gui_qt.model.project_state import ProjectState

class SettingsDialog(QDialog):
    def __init__(self, project:ProjectState, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Settings")
        self.setMinimumWidth(350)

        self.project_state = project

        main_layout = QVBoxLayout(self)
        self.build_project_form(main_layout)
        self.build_simulation_form(main_layout)
        self.build_plots_form(main_layout)
        self.build_buttons(main_layout)


    def build_project_form(self, layout):
        form = QFormLayout()
        title = QLabel("<b>Project Settings</b>")
        form.addRow(title)

        dir_path = self.project_state.directory_path
        self.dir_path_edit = QLineEdit(str(dir_path))
        form.addRow(QLabel("Directory path:"), self.dir_path_edit)

        layout.addLayout(form)

    def build_simulation_form(self, layout):
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


        self.logs_list = QListWidget()
        self.logs_list.itemChanged.connect(self._on_log_item_changed)
        self.logs_list.setSelectionMode(QListWidget.NoSelection)
        available_signals = self.project_state.get_output_signals()
        selected_signals = set(self.project_state.logging)
        for sig in available_signals:
            item = QListWidgetItem(sig)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if sig in selected_signals:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.logs_list.addItem(item)
        form.addRow("Signals logged:", self.logs_list)


        external = self.project_state.external
        external = "" if external is None else external
        self.file_edit = QLineEdit(external)
        form.addRow(QLabel("Python File:"), self.file_edit)

        layout.addLayout(form)

    def build_plots_form(self, layout):
        form = QFormLayout()
        title = QLabel("<b>Plot Settings</b>")
        form.addRow(title)
        self.title_edit = QLineEdit("")
        form.addRow(QLabel("title:"), self.title_edit)

        self.plot_list = QListWidget()
        self.plot_list.setSelectionMode(QListWidget.NoSelection)
        available_signals = self.project_state.get_output_signals()
        for sig in available_signals:
            item = QListWidgetItem(sig)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)   # TOUJOURS décoché
            self.plot_list.addItem(item)
        form.addRow("Signals in plot:", self.plot_list)

        plt_btn = QPushButton("Add")
        plt_btn.clicked.connect(self.add_plot)
        form.addRow(plt_btn)

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
        dir_path = Path(self.dir_path_edit.text())

        if not dir_path.exists():
            QMessageBox.warning(
                self,
                "Invalid directory",
                f"The directory does not exist:\n\n{dir_path}",
                QMessageBox.Ok,
            )
            return False

        # --- Simulation settings ---
        try:
            dt = float(self.dt_edit.text())
        except:
            dt = self.dt_edit.text()
        try:
            T = float(self.T_edit.text())
        except:
            T = self.T_edit.text()
        self.project_state.simulation["dt"] = dt
        self.project_state.simulation["solver"] = self.solver_combo.currentText()
        self.project_state.simulation["T"] = T
        selected = []
        for i in range(self.logs_list.count()):
            item = self.logs_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        self.project_state.logging = selected



        # --- External file ---
        file = self.file_edit.text().strip()
        self.project_state.external = None if file == "" else file

        self.accept()
        return True


    def ok(self):
        msg = self.apply()
        if msg:
            self.reject()

    def add_plot(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Invalid plot", "Plot title cannot be empty.")
            return

        signals = []
        for i in range(self.plot_list.count()):
            item = self.plot_list.item(i)
            if item.checkState() == Qt.Checked:
                signals.append(item.text())

        if not signals:
            QMessageBox.warning(self, "Invalid plot", "No signal selected.")
            return

        # --- Ensure signals are logged ---
        for sig in signals:
            if sig not in self.project_state.logging:
                self.project_state.logging.append(sig)

        self.project_state.plots.append({
            "title": title,
            "signals": signals,
        })

        # Reset UI
        self.reset_plot_form()

    def reset_plot_form(self):
        self.title_edit.clear()
        for i in range(self.plot_list.count()):
            self.plot_list.item(i).setCheckState(Qt.Unchecked)

    def _on_log_item_changed(self, item: QListWidgetItem):
        sig = item.text()

        if item.checkState() == Qt.Unchecked:
            used_in_plots = any(
                sig in plot["signals"]
                for plot in self.project_state.plots
            )

            if used_in_plots:
                QMessageBox.warning(
                    self,
                    "Signal in use",
                    f"The signal '{sig}' is used in at least one plot.\n"
                    "Remove it from plots before disabling logging."
                )
                item.setCheckState(Qt.Checked)
