from PySide6.QtWidgets import QMainWindow, QPushButton

from simulation_window import SimulationWindow


class SimulatorMain(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle('Simulator')

        self.decrement_button = QPushButton(self)
        self.decrement_button.setGeometry(150, 120, 100, 50)
        self.decrement_button.setText('Execute')
        self.decrement_button.clicked.connect(self.create)
        self.setCentralWidget(self.decrement_button)

        self.windows = []

    def create(self):
        newwin = SimulationWindow()
        self.windows.append(newwin)
        newwin.show()
