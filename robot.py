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
        self.deadlockState = False

        # detect deadlock
        # self.wait : int
        # and count wait ??

    def assignMission(self, route: list[NodePos], box: int = 0):
        self.sequence = 0
        self.route = route
        self.box = box
        if box != 0:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))

        self.doNextOperation()

    '''
    function split
    operationposwhenarrived
    operationposopponent (operationposmoving)
    '''

    # def nextOperationPos(self) -> NodePos:
    #     s = self.sequence+1
    #     if s >= len(self.route):
    #         s = len(self.route)-1
    #     return self.route[s]

    # def currOperationPos(self) -> NodePos:
    #     s = self.sequence
    #     if s >= len(self.route):
    #         s = len(self.route)-1
    #     return self.route[s]

    def currOperationPosWait(self) -> NodePos:
        # seq is not accumulated
        if self.wait:
            return self.route[self.sequence]

        # s = self.sequence
        # routelen = len(self.route)
        # if s >= routelen:
        #     return self.route[routelen-1]
        if self.sequence+1 == len(self.route):
            return self.route[self.sequence]
        return self.route[self.sequence]

    def currRobotPos(self) -> NodePos:
        s = self.sequence-1
        if s < 0:
            s = 0
        return self.route[s]

    def currRobotPosWait(self):
        if self.sequence == 0 or self.wait:
            return self.route[self.sequence]
        return self.route[self.sequence-1]

    # def proceedSequence(self):
    #     if not self.wait:
    #         self.sequence += 1
    #     self.wait = False

    # @Slot()
    # def doNextOperation(self):
    #     self.proceedSequence()

    #     if self.sequence >= len(self.route):
    #         self.finishMission()
    #         return

    #     # np = self.nextOperationPos()
    #     cp = self.currOperationPos()
    #     rp = self.currRobotPos()

    #     if rp.point() == cp.point():
    #         self.rotateOperation(cp.degree() - rp.degree(), 750)
    #     else:
    #         # self.evadeCollision()

    #         for r in self._registry:
    #             if r.robotNum == self.robotNum:
    #                 continue

    #             r_rp = r.currRobotPos()
    #             r_cp = r.currOperationPos()

    #             if cp.point() == r_rp.point():
    #                 if facingEach(cp, r_rp):
    #                     if self.robotNum < r.robotNum:
    #                         route = evaluateRoute(self.currRobotPos(), self.route[len(
    #                             self.route)-1], tempBlocked=[r_rp.point().toTuple()])

    #                         self.assignMission(route, self.box)
    #                     else:
    #                         self.waitOperation(850)
    #                     return
    #                 else:
    #                     self.waitOperation(850)
    #                     return
    #             elif cp.point() == r_cp.point():
    #                 # if facingEach(cp, r_cp):
    #                 #     if self.robotNum<r.robotNum:
    #                 #         pass
    #                 #     else:
    #                 #         self.waitOperation(850)
    #                 #         self.wait=True
    #                 # else:
    #                 #     pass
    #                 # return

    #                 # if self.robotNum < r.robotNum:
    #                 #     break
    #                 # else:
    #                 #     self.waitOperation(850)
    #                 #     self.wait = True
    #                 #     return
    #                 self.waitOperation(850)
    #                 self.wait = True
    #                 return

    #         self.moveOperation(cp.toViewPos().point(), 750)

    @Slot()
    def doNextOperation(self):
        if self.sequence + 1 == len(self.route):
            self.finishMission2()
            return

        # robot is reached this cell just right now!
        next_op_dest = self.route[self.sequence+1]
        curr_robot_pos = self.route[self.sequence]

        if curr_robot_pos.point() == next_op_dest.point():
            self.wait = False
            self.sequence += 1
            self.rotateOperation(next_op_dest.degree() -
                                 curr_robot_pos.degree(), 750)
        else:
            self.evadeCollision()

    '''
    policy type = live evasion, wait until open

    immediate reevaluate : maybe next time... when project finished
    '''

    def evadeCollision(self):
        # robot is reached just right now!
        self_op_dest = self.route[self.sequence+1]

        for r in self._registry:
            if r.robotNum == self.robotNum:
                continue

            opCurrPos = r.currRobotPosWait()
            opOperPos = r.currOperationPosWait()

            # self is finished operation just right now!
            '''
            waitoperation's destination is currrobotpos
            so seq - 1 ???
            then currrobotpos() value changes
            so.. curroperationpos() if self.wait() then route[self.seq-1]

            instead self.seq-1
            curroperationposwait() return currrobotpos()
            '''

            '''
            1 0 2
            1 wait
            2 proceed

            / 0 1
            0
            2
            '''

            if self_op_dest.point() == opOperPos.point():
                self.waitOperation(WDUR)
                return

            elif self_op_dest.point() == opCurrPos.point():
                if facingEach(self_op_dest, opCurrPos):
                    # solve deadlock
                    if self.priority() < r.priority():
                        route = evaluateRoute(self.currRobotPos(), self.route[len(
                            self.route)-1], tempBlocked=[opCurrPos.point().toTuple()])
                        self.assignMission(route, self.box)
                        return
                    else:
                        self.waitOperation(WDUR)
                        return

                else:
                    self.waitOperation(WDUR)
                    return

        self.wait = False
        self.sequence += 1
        print("robot", self.robotNum, "seq", self.sequence,
              "goto", self.route[self.sequence], self.route)
        self.moveOperation(
            self.route[self.sequence].toViewPos().point(), DUR)
        return

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

    def priority(self):
        return self.robotNum

    # def finishMission(self):
    #     if self.box:
    #         self.sequence -= 1
    #         self.dumpOperation(750)
    #     else:
    #         self.signalObj.missionFinished.emit(
    #             self.robotNum, self.currRobotPos())

    def finishMission2(self):
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
        QTimer.singleShot(duration, self.doNextOperation)


class SignalInterface(QObject):
    missionFinished = Signal(int, NodePos)

    def __init__(self) -> None:
        super().__init__()
