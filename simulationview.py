from PySide6.QtCore import QPoint, QPointF, Qt, Slot
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from cell import Cell, ChuteCell, StationCell, StationQueueCell
from pathfinding import Direction, Position
from robot import Robot

CELL_SIZE = 100


class SimulationView(QGraphicsView):
    _instance = None

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 500, 500)

        self.cells: list[Cell] = []
        self.robots: list[Robot] = []

        # get data from file
        self.drawGrid(6, 500, 500)

        chutes = [Position(4, 4, Direction.E), Position(2, 2, Direction.E)]
        self.addCell(StationCell(0, 0, 100, 100, chutes))

        self.addCell(ChuteCell(400, 400, 100, 100))
        self.addCell(ChuteCell(200, 200, 100, 100))

        self.addCell(StationQueueCell(
            100, 0, 100, 100, Position(0, 0, Direction.W)))

        self.addRobot(100, Position(0, 0, Direction.S))
        self.addRobot(100, Position(100, 0, Direction.W))

    @Slot(int, QPointF)
    def missionFinishHandler(self, num: int, position: Position):
        point = position.point()
        for cell in self.cells:
            if cell.rect().topLeft() == point:
                cell.assign(self.robots[num])
                return

        print("robotnum ", num, "cell not found on ", position.point())

    def addRobot(self, size, pos: Position):
        rect = Robot(size, len(self.robots), pos)
        self.scene.addItem(rect)
        self.robots.append(rect)

    def addCell(self, cell):
        self.scene.addItem(cell)
        self.cells.append(cell)

    def drawGrid(self, cells, height, width):
        for i in range(cells):
            self.scene.addLine(0, i*100, width, i*100)
            self.scene.addLine(i*100, 0, i*100, height)

    def start(self):
        for r in self.robots:
            r.signalObj.missionFinished.connect(self.missionFinishHandler)
            print("start ", r.nextOperationPos().x)
            r.signalObj.missionFinished.emit(r.robotNum, r.nextOperationPos())

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = SimulationView()
        return cls._instance
