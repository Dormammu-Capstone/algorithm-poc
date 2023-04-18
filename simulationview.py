from PySide6.QtCore import QPoint, QPointF, Qt, Slot
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QCloseEvent

from cell import Cell, ChuteCell, StationCell, StationQueueCell
from pathfinding import Direction, NodePos, Pos, registerMap
from robot import Robot

CELLSIZE = 100

cells1 = {'chute': [((2, 2), (1, 0))], 'workstation': [
    ((0, 0), [(2, 2)])], 'stationqueue': [((1, 0), (0, 0))]}
grid1 = (5, 6)
robots1 = [NodePos(0, 0, Direction.W), NodePos(1, 0, Direction.W)]

cells2 = {'chute': [((2, 0), (0, 0)), ((2, 1), (0, 0)), ((2, 2), (0, 2))], 'workstation': [
    ((0, 1), [(2, 0), (2, 1), (2, 2)])], 'stationqueue': [((0, 0), (0, 1)), ((0, 2), (0, 1))]}
grid2 = (6, 6)
robots2 = [NodePos(0, 0, Direction.W), NodePos(
    0, 1, Direction.W), NodePos(0, 2, Direction.N)]


class SimulationView(QGraphicsView):
    _instance = None

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.cells: list[Cell] = []
        self.robots: list[Robot] = []

        self.generateMap(cells2, grid2)
        self.deployRobots(robots2)
        # self.generateMap(cells1, grid1)
        # self.deployRobots(robots1)

    @Slot(int, NodePos)
    def missionFinishHandler(self, num: int, position: NodePos):
        for cell in self.cells:
            if cell.pos().toPoint().toTuple() == position.point().toTuple():
                cell.assign(self.robots[num])
                return

        print("runtime fatal robotnum", num,
              "cell not found on", position)

    def start(self):
        for r in self.robots:
            r.signalObj.missionFinished.connect(self.missionFinishHandler)
            r.signalObj.missionFinished.emit(
                r.robotNum, r.route[len(r.route)-1])

    def addRobot(self, size, pos: NodePos):
        rect = Robot(size, len(self.robots), pos)
        self.scene.addItem(rect)
        self.robots.append(rect)

    def addCell(self, cell: Cell):
        self.scene.addItem(cell)
        self.cells.append(cell)

    def generateMap(self, cells: dict[str, list], grid: tuple[int, int]):
        self.setSceneRect(0, 0, grid[0]*CELLSIZE, grid[1]*CELLSIZE)
        registerMap(cells, grid)

        for i in range(grid[0]+1):
            self.scene.addLine(i*CELLSIZE, 0, i*CELLSIZE, grid[1]*CELLSIZE)
        for i in range(grid[1]+1):
            self.scene.addLine(0, i*CELLSIZE, grid[0]*CELLSIZE, i*CELLSIZE)

        for a, b in cells.items():
            if a == "chute":
                for c in b:
                    self.addCell(
                        ChuteCell(c[0][0]*CELLSIZE, c[0][1]*CELLSIZE, CELLSIZE, CELLSIZE, c[1]))
            elif a == "chargingstation":
                for c in b:
                    print("add charge cell")
            elif a == "workstation":
                for c in b:
                    self.addCell(StationCell(
                        c[0][0]*CELLSIZE, c[0][1]*CELLSIZE, CELLSIZE, CELLSIZE,  c[1]))
            elif a == "stationqueue":
                for c in b:
                    self.addCell(StationQueueCell(
                        c[0][0]*CELLSIZE, c[0][1]*CELLSIZE, CELLSIZE, CELLSIZE, c[1]))
            elif a == "buffer":
                for c in b:
                    print("add buffer cell")
            elif a == "service":
                for c in b:
                    print("add service cell")
            else:
                print("nothing")
                pass

    def deployRobots(self, posList: list[NodePos]):
        for p in posList:
            self.addRobot(100, p)

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = SimulationView()
        return cls._instance
