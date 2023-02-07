from dataclasses import dataclass
from random import randrange

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsRectItem

from pathfinding import Direction, dijkstra, findRoute, getGraph
from robot import Robot


@dataclass
class Cargo:
    destination: tuple[int, int]


class Cell(QGraphicsRectItem):
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h)
        self.setBrush(color)

    def assign(self, robot):
        print("runtime fatal: ", robot, " stopped on empty cell.")


class StationCell(Cell):
    color = Qt.blue

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, self.color)
        self.setPos(x, y)

    def nextCargo(self) -> tuple[int, int]:
        # todo get cargo data from external source
        cargos = [(4, 4), (2, 2)]
        next = randrange(0, 2)
        return cargos[next]

    def assign(self, robot: Robot):
        # pos = tuple(int(ti/100) for ti in robot.pos().toTuple())
        pos = robot.lastPosition

        nodes, edges = getGraph()
        distances, prevs = dijkstra(nodes, edges, pos)
        # get chute direction from external source
        route = findRoute(
            prevs, pos, (*self.nextCargo(), Direction.E))

        robot.assignOperation(route, 8)


class StationQueueCell(Cell):
    color = Qt.darkBlue

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, self.color)

    def assign(self, robot, nextQueue):
        pass


class ChuteCell(Cell):
    color = Qt.red

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, self.color)

    def assign(self, robot):
        pos = robot.lastPosition

        nodes, edges = getGraph()
        distances, prevs = dijkstra(nodes, edges, pos)
        route = findRoute(
            prevs, pos, (0, 0, Direction.E))

        robot.assignOperation(route, None)
