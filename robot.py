from enum import Enum

import PySide6
from PySide6.QtCore import (QAbstractAnimation, QEasingCurve, QObject, QPoint,
                            QPointF, Qt, QTimer, QVariantAnimation, Signal,
                            Slot)
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView)

from pathfinding import Direction

ROBOT_EMPTY = "robot_empty.png"
ROBOT_MINERAL = "robot_mineral.png"
ROBOT_GAS = "robot_gas.png"

# instruction
ROBOT_OPERATION = Enum("ROBOT_OPERATION", "WAIT MOVE ROTATE DUMP")
ROBOT_MISSION = Enum("ROBOT_MISSION", "CARRYING RETURNING")
# qenum


# collision evasion
# if two robots are facing each
# lower priority go around
# if two robots will not face (ㄱ)
# lower priority wait
# if two robots will face
# lower priority go around


class Robot(QGraphicsPixmapItem):
    def __init__(self, position, size, robotNum):
        super().__init__(QPixmap(ROBOT_EMPTY).scaled(size, size))
        self.setPos(position[0], position[1])
        self.setTransformOriginPoint(size/2, size/2)
        self.setRotation((position[2]+1)*90)

        self.lastPosition = position
        # todo: currentdestination/nextposition/currentposition
        # this program set the operations -move rotate- first
        # when assign the task
        # change :
        # just generate next operation every time
        # every call on doNextOperation

        self.signalObj = SignalInterface()
        self.robotNum = robotNum

        self.sequence = 0
        self.queue = []
        self.box = None
        self.mission = ROBOT_MISSION.RETURNING

    def getPosition(self):
        pass

    def assignOperation(self, route, box):
        self.sequence = 0
        self.queue = []

        if box != None:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))
            self.box = box
        # else:
        #     self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))

        # o in route : (x,y,direction)
        # maybe this is useless...
        for o in route:
            if self.lastPosition[2] == o[2]:
                self.queue.append(
                    (ROBOT_OPERATION.MOVE, QPoint(o[0]*100, o[1]*100)))
            else:
                degreeInterval = self.lastPosition[2]-o[2]
                if degreeInterval == 1 or degreeInterval == -3:
                    self.queue.append((ROBOT_OPERATION.ROTATE, -90))
                elif degreeInterval == -1 or degreeInterval == 3:
                    self.queue.append((ROBOT_OPERATION.ROTATE, 90))
                else:
                    self.queue.append((ROBOT_OPERATION.ROTATE, 90))
                    self.queue.append((ROBOT_OPERATION.ROTATE, 90))
            self.lastPosition = o

        self.doNextOperation()

    # todo: get weight from another source
    @Slot()
    def doNextOperation(self):
        if self.sequence == len(self.queue):
            if self.box:
                self.dumpOperation(750)
            else:
                self.signalObj.operationFinished.emit(
                    self.robotNum, self.pos())
            return

        currentStep = self.queue[self.sequence]
        if currentStep[0] == ROBOT_OPERATION.MOVE:
            self.moveAnimation(currentStep[1], 750)
        elif currentStep[0] == ROBOT_OPERATION.ROTATE:
            self.rotateAnimation(currentStep[1], 750)

        self.sequence += 1

    def rotateAnimation(self, degree, duration):
        anim = QVariantAnimation(self.signalObj)
        currRot = int(self.rotation())
        anim.setStartValue(currRot)
        anim.setEndValue(currRot+degree)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        # anim.valueChanged.connect(self.rotateOperationSlot)
        anim.valueChanged.connect(self.setRotation)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def moveAnimation(self, destination, duration):
        anim = QVariantAnimation(self.signalObj)
        anim.setStartValue(QPoint(int(self.pos().x()), int(self.pos().y())))
        anim.setEndValue(destination)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        # anim.valueChanged.connect(self.moveFinished)
        anim.valueChanged.connect(self.setPos)
        anim.finished.connect(self.doNextOperation)
        # anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    @Slot(QPointF)
    def moveFinished(self, point: QPointF):
        self.setPos(point)
        self.lastPosition = (point.x(), point.y(), self.lastPosition[2])

    @Slot(int)
    def rotateOperationSlot(self, angle):
        self.setRotation(angle)
        if angle-self.lastPosition[2] == 1:
            pass

    def dumpOperation(self, duration):
        self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
        self.box = None
        self.waitOperation(duration)

    def waitOperation(self, duration):
        QTimer.singleShot(duration, self.doNextOperation)


class SignalInterface(QObject):
    operationFinished = Signal(int, QPointF)

    def __init__(self) -> None:
        super().__init__()
