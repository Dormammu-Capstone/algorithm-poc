from enum import Enum

import PySide6
from PySide6.QtCore import (QAbstractAnimation, QEasingCurve, QObject, QPoint,
                            Qt, QVariantAnimation, Signal, Slot)
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView)

from pathfinding import Direction

ROBOT_EMPTY = "robot_empty.png"
ROBOT_MINERAL = "robot_mineral.png"
ROBOT_GAS = "robot_gas.png"

ROBOT_OPERATION = Enum("ROBOT_OPERATION", "WAIT MOVE ROTATE DUMP")


class Robot(QGraphicsPixmapItem):
    def __init__(self, position, size, robotNum):
        super().__init__(QPixmap(ROBOT_EMPTY).scaled(size, size))
        self.setPos(position[0], position[1])
        self.setTransformOriginPoint(size/2, size/2)
        self.setRotation((position[2]+1)*90)
        self.lastPosition = position
        # currentdestination

        self.signalObj = SignalInterface()
        self.robotNum = robotNum

        self.sequence = 0
        self.queue = []
        # sequence for collision mitigation to insert wait
        self.box = False

    # todo: dump when robot has box
    # todo: give box information to robot
    def assignOperation(self, route, box):
        self.sequence = 0
        self.queue = []

        if box:
            self.setPixmap(QPixmap(ROBOT_GAS).scaled(100, 100))
        else:
            self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
        self.box = box

        # todo: optimize routing
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
        if len(self.queue) == self.sequence:
            self.setPixmap(QPixmap(ROBOT_EMPTY).scaled(100, 100))
            self.signalObj.operationFinished.emit(self.robotNum)
            return

        currentStep = self.queue[self.sequence]
        if currentStep[0] == ROBOT_OPERATION.MOVE:
            self.moveAnimation(self.signalObj, currentStep[1], 750)
        elif currentStep[0] == ROBOT_OPERATION.ROTATE:
            self.rotateAnimation(self.signalObj, currentStep[1], 750)

        self.sequence += 1

    def rotateAnimation(self, parent, degree, duration):
        anim = QVariantAnimation(parent)
        currRot = int(self.rotation())
        anim.setStartValue(currRot)
        anim.setEndValue(currRot+degree)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.valueChanged.connect(self.setRotation)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def moveAnimation(self, parent, destination, duration):
        anim = QVariantAnimation(parent)
        anim.setStartValue(QPoint(int(self.pos().x()), int(self.pos().y())))
        anim.setEndValue(destination)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.valueChanged.connect(self.setPos)
        anim.finished.connect(self.doNextOperation)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def dump(self):
        pass

    def wait(self):
        pass


class SignalInterface(QObject):
    operationFinished = Signal(int)

    def __init__(self) -> None:
        super().__init__()
