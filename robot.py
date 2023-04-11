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
WDUR = 850

DEAD_THRESHOLD = 7


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
        self.priority = robotNum

        self.wait = False
        self.deadlockedCounter = 0

        # detect deadlock
        # self.wait : int
        # and count wait ??

    def assignMission(self, route: list[NodePos], box: int = 0):
        self.sequence = 0
        self.route = route
        self.priority = self.robotNum
        self.box = box
        if box != 0:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))

        self.doNextOperation()

    '''
    function split
    operationposwhenarrived
    operationposopponent (operationposmoving)
    '''

    def currOperationPosWait(self) -> NodePos:
        # seq is not accumulated
        if self.wait:
            return self.route[self.sequence]

        if self.sequence+1 == len(self.route):
            return self.route[self.sequence]
        return self.route[self.sequence]

    def currRobotPosWait(self):
        if self.sequence == 0 or self.wait:
            return self.route[self.sequence]
        return self.route[self.sequence-1]

    @Slot()
    def doNextOperation(self):
        if self.sequence + 1 == len(self.route):
            self.finishMission()
            return

        if self.deadlockedCounter >= DEAD_THRESHOLD:
            # this idea is not testable
            # find all robots
            bots: list[Robot] = []
            selfPos = self.route[self.sequence].point().toTuple()
            for r in self._registry:
                neighborPos = r.route[r.sequence].point().toTuple()
                if r.wait:
                    if neighborPos == (selfPos[0], selfPos[1]-1) or neighborPos == (selfPos[0], selfPos[1]+1) or neighborPos == (selfPos[0]-1, selfPos[1]) or neighborPos == (selfPos[0]+1, selfPos[1]):
                        bots.append(r)

            for r in bots:
                # i think tempblocked should be nodepos
                # each cell can assign "align" mission to robot
                # to dump or get box
                route = evaluateRoute(r.route[r.sequence], r.route[len(
                    r.route)-1], tempBlocked=[r.route[r.sequence+1].point().toTuple()])
                r.assignMission()

        # robot is reached this cell just right now!
        degreeDiff = self.route[self.sequence +
                                1].degree()-self.route[self.sequence].degree()

        if degreeDiff != 0:
            self.wait = False
            self.sequence += 1
            self.rotateOperation(degreeDiff, 750)
        else:
            self.evadeCollision()

    '''
    policy type = live evasion, wait until open

    immediate reevaluate : maybe next time... when project finished
    '''

    def evadeCollision(self):
        self_op_dest = self.route[self.sequence+1]

        for r in self._registry:
            if r.robotNum == self.robotNum:
                continue

            opCurrPos = r.currRobotPosWait()
            opOperPos = r.currOperationPosWait()

            # maybe do not use of these...

            '''
            1 0 2
            1 wait
            2 proceed

            / 0 1
            0
            2
            '''
            # self is finished operation just right now!
            # self.seq is not accumulated!

            if not r.wait and self_op_dest.point() == opOperPos.point():
                print("op")
                self.waitOperation(WDUR)
                return

            elif self_op_dest.point() == opCurrPos.point():
                if facingEach(self_op_dest, opCurrPos):
                    print("facing")

                    # if tempblocked is one of deadlocked robots destination??
                    if self.route[len(self.route)-1].point() == opCurrPos.point():
                        self.priority += 1

                    if self.priority < r.priority:
                        # call maybe..upper conflict resolver?
                        print("evaluate")
                        # if tempblocked is one of deadlocked robots destination??
                        # tempblocked should be nodepos?
                        route = evaluateRoute(self.route[self.sequence], self.route[len(
                            self.route)-1], tempBlocked=[opCurrPos.point().toTuple()])
                        self.assignMission(route, self.box)
                        return
                    else:
                        print(self.robotNum, "evaluate else",
                              self.priority, r.priority)
                        self.waitOperation(WDUR)
                        return

                else:
                    print("not facing")
                    self.waitOperation(WDUR)
                    return

        self.wait = False
        self.sequence += 1
        self.moveOperation(
            self.route[self.sequence].toViewPos().point(), DUR)
        return

    def finishMission(self):
        if self.box:
            self.dumpOperation(750)
        else:
            self.signalObj.missionFinished.emit(
                self.robotNum, self.route[len(self.route)-1])

    def rotateOperation(self, degree: int, duration: int):
        anim = QVariantAnimation(self.signalObj)
        currRot = int(self.rotation())
        anim.setStartValue(currRot)
        anim.setEndValue(currRot+degree)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setRotation)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def moveOperation(self, destination: QPoint, duration: int):
        self.deadlockedCounter = 0

        anim = QVariantAnimation(self.signalObj)
        anim.setStartValue(QPoint(int(self.pos().x()), int(self.pos().y())))
        anim.setEndValue(destination)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.valueChanged.connect(self.setPos)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def dumpOperation(self, duration: int):
        self.wait = True
        self.box = 0
        self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
        QTimer.singleShot(duration, self.doNextOperation)

    def waitOperation(self, duration: int):
        self.wait = True
        self.deadlockedCounter += 1
        print(self.robotNum, "wait", self.route)
        print(self.robotNum, "deadlock", self.deadlockedCounter)
        QTimer.singleShot(duration, self.doNextOperation)


class SignalInterface(QObject):
    missionFinished = Signal(int, NodePos)

    def __init__(self) -> None:
        super().__init__()
