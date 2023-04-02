# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from db import queryMap

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    cells, grid = queryMap("test")
    registerMap(cells, grid)
    mainWindow.view.generateMap(cells, grid)

    mainWindow.view.start()
    mainWindow.show()

    sys.exit(app.exec())
