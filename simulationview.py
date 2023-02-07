from PySide6.QtCore import QPointF, Qt, Slot
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

import pathfinding
from cell import Cell, ChuteCell, StationCell, StationQueueCell
from robot import ROBOT_MISSION, Robot


class SimulationView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 500, 500)

        self.cells: list[Cell] = []
        self.drawGrid(6, 500, 500)
        self.addCell(StationCell(0, 0, 100, 100))
        self.addCell(ChuteCell(400, 400, 100, 100))
        self.addCell(ChuteCell(200, 200, 100, 100))
        self.addCell(StationQueueCell(100, 0, 100, 100))

        self.robots = []
        self.addRobot(0, 0, 100)

    def start(self):
        self.robots[0].signalObj.operationFinished.connect(
            self.operationFinishHandler)
        # self.operationFinishHandler(0,)
        self.robots[0].signalObj.operationFinished.emit(
            0, self.robots[0].pos())

    @Slot(int, QPointF)
    def operationFinishHandler(self, num, point):
        pos = self.robots[num].lastPosition

        nodes, edges = pathfinding.getGraph()
        distances, prevs = pathfinding.dijkstra(
            nodes, edges, pos)

        for cell in self.cells:
            if cell.rect().topLeft().__eq__(point):
                cell.assign(self.robots[num])
                break

    def addRobot(self, x, y, size):
        rect = Robot((x, y, pathfinding.Direction.S), size, len(self.robots))
        self.scene.addItem(rect)
        self.robots.append(rect)

    def addCell(self, cell):
        self.scene.addItem(cell)
        self.cells.append(cell)

    def drawGrid(self, cells, height, width):
        for i in range(cells):
            self.scene.addLine(0, i*100, width, i*100)
            self.scene.addLine(i*100, 0, i*100, height)
