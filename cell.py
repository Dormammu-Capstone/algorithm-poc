from random import randrange

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsRectItem

from pathfinding import Direction, Position, dijkstra, findRoute, getGraph
from robot import Robot


class Cell(QGraphicsRectItem):
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h)
        self.setBrush(color)

    def assign(self, robot: Robot):
        print("runtime fatal: ", robot.robotNum,
              " calling assign on empty cell.")


class StationCell(Cell):
    color = Qt.blue

    def __init__(self, x, y, w, h, chutesPos: list[Position]):
        super().__init__(x, y, w, h, self.color)
        self.setPos(x, y)
        self.chutesPos = chutesPos

    def nextCargo(self) -> Position:
        next = randrange(0, len(self.chutesPos))
        return self.chutesPos[next]

    def assign(self, robot: Robot):
        pos = robot.currRobotPos().toGrid()

        nodes, edges = getGraph()
        distances, prevs = dijkstra(nodes, edges, pos)
        route = findRoute(
            prevs, pos, self.nextCargo().toTuple())

        print(robot.robotNum, ttor(route))

        robot.assignMission(ttor(route), 8)


class StationQueueCell(Cell):
    color = Qt.darkBlue

    def __init__(self, x, y, w, h, nextQueue: Position):
        super().__init__(x, y, w, h, self.color)
        self.nextQueue: Position = nextQueue

    def assign(self, robot):
        pos = robot.currRobotPos().toGrid()

        nodes, edges = getGraph()
        distances, prevs = dijkstra(nodes, edges, pos)
        route = findRoute(
            prevs, pos, self.nextQueue.toTuple())

        print(robot.robotNum, ttor(route))

        robot.assignMission(ttor(route), 0)


class ChuteCell(Cell):
    color = Qt.red

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, self.color)

    def assign(self, robot):
        pos = robot.currRobotPos().toGrid()

        nodes, edges = getGraph()
        distances, prevs = dijkstra(nodes, edges, pos)
        route = findRoute(
            prevs, pos, (1, 0, Direction.W))

        print(robot.robotNum, ttor(route))

        robot.assignMission(ttor(route), 0)

# tuple to route


def ttor(route) -> list[Position]:
    res = []
    for i in route:
        res.append(Position(i[0], i[1], i[2]))

    return res
