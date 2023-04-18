# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Slot, Qt
from db import queryMap
from PySide6.QtGui import QCloseEvent

from pathfinding import Pos, ViewPos, backTrack, dijkstra, generateGraph, registerMap
from simulationview import SimulationView
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.view = SimulationView.getInstance()
        self.setCentralWidget(self.view)

        self.setAttribute(Qt.WA_DeleteOnClose, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.setWindowTitle("newtitle")

    mainWindow.show()
    mainWindow.view.start()

    second = QMainWindow()
    second.setWindowTitle("hello new window")
    second.show()

    sys.exit(app.exec())
