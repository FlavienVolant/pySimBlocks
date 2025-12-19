import sys
from PySide6.QtWidgets import QApplication
from pySimBlocks.gui_qt.main_window import MainWindow


# ============================================================
# Entry point
# ============================================================
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1100, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
