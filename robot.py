from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (QAbstractAnimation, QEasingCurve, QObject, QPoint,
                            QPointF, Qt, QTimer, QVariantAnimation, Signal,
                            Slot)
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView)

from pathfinding import Direction, Position, dijkstra, findRoute, getGraph

ROBOT_EMPTY = "image/robot_empty.png"
ROBOT_MINERAL = "image/robot_mineral.png"
ROBOT_GAS = "image/robot_gas.png"

ROBOT_INSTRUCTION = Enum("ROBOT_OPERATION", "WAIT MOVE ROTATE DUMP")
ROBOT_MISSION = Enum("ROBOT_MISSION", "CARRYING RETURNING")

DUR = 750


class Robot(QGraphicsPixmapItem):
    _registry: list[Robot] = []

    def __init__(self,  size: int, robotNum: int, position: Position):
        self._registry.append(self)

        super().__init__(QPixmap(ROBOT_EMPTY).scaled(size, size))
        self.setPos(position.x, position.y)
        self.setTransformOriginPoint(size/2, size/2)
        self.setRotation(position.degree())

        self.signalObj = SignalInterface()
        self.robotNum = robotNum

        self.sequence = 0
        self.route = [position]
        self.box = None

        print("init", position.x)

    '''
    ->
    O O O O
    1R2 3
    1 : can be currpos
    2 : curroppos
    3 : nextoppos 

    O O O O
      R 
    1 2 3 4
    seq is 2
    if r arrived cell
    emit operation finish -> donextop
    r seq become 3 
    3 is curroppos
    4 is nextoppos

    tongill with *100 here

    '''

    def nextOperationPos(self) -> Position:
        s = self.sequence+1
        if s >= len(self.route):
            s -= 1
        # return self.route[s]
        return self.route[s].toView()

    def currOperationPos(self) -> Position:
        return self.route[self.sequence].toView()

    def currRobotPos(self) -> Position:
        p = self.pos()
        return Position(p.x(), p.y(), (self.rotation()/90) % 4)

    def assignMission(self, route: list[Position], box: int = 0):
        self.sequence = 0
        self.route = route
        self.box = box

        if box != 0:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))

        self.doNextOperation()

    @Slot()
    def doNextOperation(self):
        self.sequence += 1

        if self.sequence == len(self.route):
            print(self.robotNum, "route finished")
            if self.box:
                self.dumpOperation(750)
            else:
                self.signalObj.missionFinished.emit(
                    self.robotNum, self.currRobotPos())
            return

        np = self.nextOperationPos()
        cp = self.currOperationPos()
        rp = self.currRobotPos()

        if rp.point() == cp.point():
            print(self.robotNum, "rotate")
            self.rotateAnimation(rp.degreeTo(cp), 750)
        else:
            # avoid collision
            # should i make scheduler on simulationview?
            for r in self._registry:
                # if self.curroppos is r.curroppos and facing 1 0 2
                oppocp = r.currOperationPos()
                opporp = r.currRobotPos()
                # if cp.point() == oppocp.point() and (cp.direction+oppocp.direction) % 2 == 0:
                if cp.point() == oppocp.point():
                    if self.robotNum < r.robotNum:
                        # go around
                        pos = self.currRobotPos().toGrid()
                        nodes, edges = getGraph([oppocp.point().toTuple()])
                        dist, prevs = dijkstra(nodes, edges, pos)
                        nr = findRoute(
                            prevs, pos, self.route[len(self.route)-1].toTuple())
                        self.assignMission(nr, self.box)
                        return
                    else:
                        self.waitOperation(DUR)
                        return
                # if self.curroppos is r.currobotpos and facing 1 2
                # elif cp.point() == opporp.point() and (cp.direction+opporp.direction) % 2 == 0:
                elif cp.point() == opporp.point():
                    if (cp.direction+opporp.direction) % 2 == 0:
                        if self.robotNum < r.robotNum:
                            pos = self.currRobotPos().toGrid()
                            nodes, edges = getGraph([oppocp.point().toTuple()])
                            dist, prevs = dijkstra(nodes, edges, pos)
                            nr = findRoute(
                                prevs, pos, self.route[len(self.route)-1].toTuple())
                            self.assignMission(nr, self.box)
                            return
                        else:
                            self.waitOperation(DUR)
                            return
                    else:
                        self.waitOperation(DUR)
                        return
            print(self.robotNum, "move")
            self.moveAnimation(cp.point(), DUR)

    # def predictCollision(self)->bool:
        '''
        policy type : live evasion
        (other type is predict with every robot route)

        collision evasion
        if two robots are facing each
        lower priority go around

        if robots have two cells between 1 O O 2
        two next position are against
        one go around
        lets go simple - 1 2

        -- 1s perspective --
        1s next is 2s current opposite direction

        if robots have one cell between 1 O 2
        1s next is 2s next
        one go around

        1 0 2
        if 2 go and turn left/right
        no i think this may solved by 1st solution

        if two robots not face (ㄱ)
        lower priority wait
        '''

    def rotateAnimation(self, degree, duration):
        anim = QVariantAnimation(self.signalObj)
        currRot = int(self.rotation())
        anim.setStartValue(currRot)
        anim.setEndValue(currRot+degree)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setRotation)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def moveAnimation(self, destination, duration):
        anim = QVariantAnimation(self.signalObj)
        anim.setStartValue(QPoint(int(self.pos().x()), int(self.pos().y())))
        anim.setEndValue(destination)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setPos)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def dumpOperation(self, duration):
        self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
        self.box = 0
        self.waitOperation(duration)

    def waitOperation(self, duration):
        QTimer.singleShot(duration, self.doNextOperation)


class SignalInterface(QObject):
    missionFinished = Signal(int, Position)

    def __init__(self) -> None:
        super().__init__()
