from random import randrange

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QGraphicsRectItem, QPushButton

from pathfinding import (Direction, NodePos, Pos, ViewPos, backTrack, dijkstra,
                         evaluateRoute, evaluateRouteToCell, generateGraph)
from robot import Robot


class Cell(QGraphicsRectItem):
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h)
        self.setBrush(color)
        self.setPos(x//100, y//100)
        # button = QPushButton('test', self)
        # button.clicked.connect(QCoreApplication.instance().quit)
        

    def assign(self, robot: Robot):
        print("error in cell.py :", robot.robotNum,
              "called assign function on empty cell")


class StationCell(Cell):
    color = Qt.blue

    def __init__(self, x, y, w, h, chutesPos: list[tuple[int, int]]):
        super().__init__(x, y, w, h, self.color)
        self.chutesPos = chutesPos

    def nextCargo(self) -> tuple[int, int]:
        next = randrange(0, len(self.chutesPos))
        return self.chutesPos[next]

    def assign(self, robot: Robot):
        route = evaluateRouteToCell(
            robot.route[len(robot.route)-1], self.nextCargo())
        robot.assignMission(route, 8)


class StationQueueCell(Cell):
    color = Qt.darkBlue

    def __init__(self, x, y, w, h, nextQueue: tuple[int, int]):
        super().__init__(x, y, w, h, self.color)
        self.nextQueue = nextQueue

    def assign(self, robot: Robot):
        route = evaluateRouteToCell(
            robot.route[len(robot.route)-1], self.nextQueue)
        robot.assignMission(route, 0)


class ChuteCell(Cell):
    color = Qt.red

    def __init__(self, x, y, w, h, returnPos: tuple[int, int]):
        super().__init__(x, y, w, h, self.color)
        self.returnPos = returnPos

    def assign(self, robot: Robot):
        route = evaluateRouteToCell(
            robot.route[len(robot.route)-1], self.returnPos)
        robot.assignMission(route, 0)
