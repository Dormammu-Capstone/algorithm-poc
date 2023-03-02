from random import randrange

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsRectItem

from pathfinding import (Direction, NodePos, Pos, ViewPos, backTrack, dijkstra,
                         evaluateRoute, generateGraph)
from robot import Robot


class Cell(QGraphicsRectItem):
    def __init__(self, x, y, w, h, dir, color):
        super().__init__(x, y, w, h)
        self.setBrush(color)
        self.nodePos = ViewPos(x, y, dir).toNodePos()

    def assign(self, robot: Robot):
        print("runtime fatal: ", robot.robotNum,
              " calling assign on empty cell.")


class StationCell(Cell):
    color = Qt.blue

    def __init__(self, x, y, w, h, dir, chutesPos: list[Pos]):
        super().__init__(x, y, w, h, dir, self.color)
        self.setPos(x, y)
        self.chutesPos = chutesPos

    def nextCargo(self) -> NodePos:
        next = randrange(0, len(self.chutesPos))
        return self.chutesPos[next]

    def assign(self, robot: Robot):
        route = evaluateRoute(self.nodePos, self.nextCargo())
        robot.assignMission(route, 8)


class StationQueueCell(Cell):
    color = Qt.darkBlue

    def __init__(self, x, y, w, h, dir, nextQueue: NodePos):
        super().__init__(x, y, w, h, dir, self.color)
        self.nextQueue: NodePos = nextQueue

    def assign(self, robot):
        route = evaluateRoute(self.nodePos, self.nextQueue)
        robot.assignMission(route, 0)


class ChuteCell(Cell):
    color = Qt.red

    # returnpos maybe found dynamically
    def __init__(self, x, y, w, h, dir, returnPos: NodePos):
        super().__init__(x, y, w, h, dir, self.color)
        self.returnPos = returnPos

    def assign(self, robot):
        route = evaluateRoute(self.nodePos, self.returnPos)
        robot.assignMission(route, 0)
