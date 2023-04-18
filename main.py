import sys
from PySide6.QtWidgets import QApplication

from newmainwindow import SimulatorMain

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimulatorMain()
    win.show()

    sys.exit(app.exec())
