from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (QAbstractAnimation, QEasingCurve, QObject, QPoint,
                            QPointF, Qt, QTimer, QVariantAnimation, Signal,
                            Slot)
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView)

from pathfinding import (NodePos, backTrack, dijkstra, evaluateRoute,
                         facingEach, generateGraph)

ROBOT_EMPTY = "image/robot_empty.png"
ROBOT_MINERAL = "image/robot_mineral.png"
ROBOT_GAS = "image/robot_gas.png"

ROBOT_INSTRUCTION = Enum("ROBOT_OPERATION", "WAIT MOVE ROTATE DUMP")
ROBOT_MISSION = Enum("ROBOT_MISSION", "CARRYING RETURNING")

DUR = 750


class Robot(QGraphicsPixmapItem):
    _registry: list[Robot] = []

    def __init__(self,  size: int, robotNum: int, position: NodePos):
        self._registry.append(self)

        super().__init__(QPixmap(ROBOT_EMPTY).scaled(size, size))
        self.setPos(position.toViewPos().x, position.toViewPos().y)
        self.setTransformOriginPoint(size/2, size/2)
        self.setRotation(position.degree())

        self.signalObj = SignalInterface()
        self.robotNum = robotNum

        self.box = 0
        self.sequence = 0
        self.route = [position]

        self.wait = False

    def assignMission(self, route: list[NodePos], box: int = 0):
        self.sequence = 0
        self.route = route
        self.box = box

        if box != 0:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))

        self.doNextOperation()

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

    '''
    ---->
    1 2 3
     R
    
    1:currrobot
    2:curroppos
    3:nextoppos
    '''

    def nextOperationPos(self) -> NodePos:
        s = self.sequence+1
        if s >= len(self.route):
            s = len(self.route)-1
        return self.route[s]

    def currOperationPos(self) -> NodePos:
        s = self.sequence
        if s >= len(self.route):
            s = len(self.route)-1
        return self.route[s]

    def currRobotPos(self) -> NodePos:
        s = self.sequence-1
        if s < 0:
            s = 0
        return self.route[s]

    # if robot is dumping
    # seq=n-1
    # nextoppos=n-1
    # curroppos=n-1
    # currrobotpos=n-2
    # shit

    @Slot()
    def doNextOperation(self):
        if not self.wait:
            self.sequence += 1

        self.wait = False
        # print("robot", self.robotNum, "seq", self.sequence)

        if self.sequence >= len(self.route):
            self.sequence -= 1
            if self.box:
                self.dumpOperation(750)
            else:
                self.signalObj.missionFinished.emit(
                    self.robotNum, self.currOperationPos())
            return

        # np = self.nextOperationPos()
        cp = self.currOperationPos()
        rp = self.currRobotPos()

        if rp.point() == cp.point():
            self.rotateAnimation(cp.degree() - rp.degree(), 750)
        else:

            for r in self._registry:
                if r.robotNum == self.robotNum:
                    continue

                r_rp = r.currRobotPos()
                r_cp = r.currOperationPos()

                if cp.point() == r_rp.point():
                    if facingEach(cp, r_rp):
                        if self.robotNum < r.robotNum:
                            route = evaluateRoute(self.currRobotPos(), self.route[len(
                                self.route)-1], tempBlocked=[r_rp.point().toTuple()])

                            self.assignMission(route, self.box)
                        else:
                            self.waitOperation(850)
                            self.wait = True
                        return
                    else:
                        self.waitOperation(850)
                        self.wait = True
                        return
                elif cp.point() == r_cp.point():
                    # if facingEach(cp, r_cp):
                    #     if self.robotNum<r.robotNum:
                    #         pass
                    #     else:
                    #         self.waitOperation(850)
                    #         self.wait=True
                    # else:
                    #     pass
                    # return

                    # if self.robotNum < r.robotNum:
                    #     break
                    # else:
                    #     self.waitOperation(850)
                    #     self.wait = True
                    #     return
                    self.waitOperation(850)
                    self.wait = True
                    return

            self.moveAnimation(cp.toViewPos().point(), 750)

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

    def rotateAnimation(self, degree: int, duration: int):
        anim = QVariantAnimation(self.signalObj)
        currRot = int(self.rotation())
        anim.setStartValue(currRot)
        anim.setEndValue(currRot+degree)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setRotation)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def moveAnimation(self, destination: QPoint, duration: int):
        anim = QVariantAnimation(self.signalObj)
        anim.setStartValue(QPoint(int(self.pos().x()), int(self.pos().y())))
        anim.setEndValue(destination)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setPos)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def dumpOperation(self, duration: int):
        self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
        self.box = 0
        QTimer.singleShot(duration, self.doNextOperation)

    def waitOperation(self, duration: int):
        QTimer.singleShot(duration, self.doNextOperation)


class SignalInterface(QObject):
    missionFinished = Signal(int, NodePos)

    def __init__(self) -> None:
        super().__init__()
