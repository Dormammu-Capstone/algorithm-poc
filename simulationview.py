from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

import pathfinding
from robot import Robot


class SimulationView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 500, 500)

        # todo: get init state from database
        self.drawGrid(6, 500, 500)

        self.robots = []
        self.addRobot(0, 0, 100)

    def start(self):
        # testing
        # 0,0 <-> 4,4
        self.robots[0].signalObj.operationFinished.connect(
            self.operationFinishHandler)
        self.operationFinishHandler(0)

    # todo: cache route
    @Slot(int)
    def operationFinishHandler(self, num):
        pos = self.robots[num].lastPosition

        nodes, edges = pathfinding.generateGraph()
        distances, prevs = pathfinding.dijkstra(
            nodes, edges, pos)

        if self.robots[num].box:
            route = pathfinding.findRoute(
                prevs, pos, (0, 0, pathfinding.Direction.E))
            self.robots[num].assignOperation(route, False)
        else:
            route = pathfinding.findRoute(
                prevs, pos, (4, 4, pathfinding.Direction.N))
            self.robots[num].assignOperation(route, True)

    def addRobot(self, x, y, size):
        rect = Robot((x, y, pathfinding.Direction.S), size, len(self.robots))
        self.scene.addItem(rect)
        self.robots.append(rect)

    # todo: cell width height, xcells ycells
    # todo: get info from database
    def drawGrid(self, cells, height, width):
        for i in range(cells):
            self.scene.addLine(0, i*100, width, i*100)
            self.scene.addLine(i*100, 0, i*100, height)
