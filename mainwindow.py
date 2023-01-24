# This Python file uses the following encoding: utf-8
import heapq
import os
import sys
import time
from enum import Enum

import PySide6.QtCore as QtCore
from PySide6.QtCore import (QAbstractAnimation, QEasingCurve,
                            QParallelAnimationGroup, QPoint,
                            QPropertyAnimation, QVariantAnimation, Slot)
from PySide6.QtGui import QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

import pathfinding
from robot import ROBOT_OPERATION, Robot
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

        self.view = SimulationView()
        self.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.view.start()
    mainWindow.show()

    sys.exit(app.exec())
