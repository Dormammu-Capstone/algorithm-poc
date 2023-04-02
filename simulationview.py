from PySide6.QtCore import QPoint, QPointF, Qt, Slot
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from cell import Cell, ChuteCell, StationCell, StationQueueCell
from pathfinding import Direction, NodePos, Pos
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

        # ### self.generateMap()
        self.drawGrid(6, 500, 500)

        chutes = [(2, 2)]
        # chutes = [NodePos(4, 4, Direction.S), NodePos(2, 2, Direction.S)]

        self.addCell(StationCell(0, 0, 100, 100,  chutes))
        self.addCell(StationQueueCell(
            100, 0, 100, 100, (0, 0)))

        # self.addCell(ChuteCell(400, 400, 100, 100, (1, 0)))
        self.addCell(ChuteCell(200, 200, 100, 100, (1, 0)))
        # ### self.generateMap()

        self.addRobot(100, NodePos(0, 0, Direction.W))
        self.addRobot(100, NodePos(1, 0, Direction.W))

    @Slot(int, NodePos)
    def missionFinishHandler(self, num: int, position: NodePos):
        for cell in self.cells:
            if cell.pos().toPoint().toTuple() == position.point().toTuple():
                cell.assign(self.robots[num])
                return

        print("runtime fatal robotnum", num,
              "cell not found on", position)

    def start(self):
        # self.generateMap()

        for r in self.robots:
            r.signalObj.missionFinished.connect(self.missionFinishHandler)
            r.signalObj.missionFinished.emit(
                r.robotNum, r.route[len(r.route)-1])
            # r.signalObj.missionFinished.emit(r.robotNum, r.currRobotPos())

    def addRobot(self, size, pos: NodePos):
        rect = Robot(size, len(self.robots), pos)
        self.scene.addItem(rect)
        self.robots.append(rect)

    def addCell(self, cell: Cell):
        self.scene.addItem(cell)
        self.cells.append(cell)

    def drawGrid(self, cells, height, width):
        for i in range(cells):
            self.scene.addLine(0, i*100, width, i*100)
            self.scene.addLine(i*100, 0, i*100, height)

    def generateMap(self, cells: dict[str, list], grid: tuple[int, int]):
        self.setSceneRect(0, 0, grid[0]*100, grid[1]*100)

        # drawgrid
        # new drawgrid func needed
        for i in range(grid[0]+1):
            print("draw line", i)
        for i in range(grid[1]+1):
            print("draw line", i)

        # addcell
        for a, b in cells.items():
            if a == "chute":
                for c in b:
                    # self.addCell(Cell(c))
                    print("add chute cell", c)
            elif a == "chargingstation":
                for c in b:
                    print("add charge cell")
            elif a == "workstation":
                for c in b:
                    print("add work cell")
            elif a == "buffer":
                for c in b:
                    print("add buffer cell")
            elif a == "service":
                for c in b:
                    print("add service cell")
            else:
                print("nothing")
                pass

        # addrobot
        # self.addRobot(100, NodePos(0, 0, 0))

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = SimulationView()
        return cls._instance
