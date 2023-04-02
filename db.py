import pymysql
import sys
import robot
import pathfinding
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

conn = pymysql.connect(host='127.0.0.1', user='root',
                       password='root', db='lghpdb', charset='utf8')

dblist = ['buffer', 'chargingstation', 'chute', 'workstation', 'service']
colors = [Qt.red, Qt.blue, Qt.green, Qt.white]


def queryMap(mapName: str):
    sql = 'select locationx, locationy from '
    cells = {}
    grid = ()

    with conn.cursor() as cur:
        for l in dblist:
            cur.execute(sql + l)
            result = cur.fetchall()
            templist = []
            for data in result:
                templist.append((data[1], data[0]))
            cells[l] = templist

        cur.execute(
            'select gridsizex, gridsizey from grid where grid_id = %s', [mapName])
        result = cur.fetchall()
        for data in result:
            grid = data

    return cells, grid


# cells, grid = queryMap("test")

# app = QApplication()
# mainwindow = QMainWindow()

# view = QGraphicsView()
# scene = QGraphicsScene()
# scene.setSceneRect(0, 0, grid[0]*100, grid[1]*100)
# for i in range(grid[0]+1):
#     scene.addLine(i*100, 0, i*100, grid[1]*100)
# for i in range(grid[1]+1):
#     scene.addLine(0, i*100, grid[0]*100, i*100)

# bot1 = robot.Robot(100, 0, pathfinding.NodePos(3, 3, 0))
# bot2 = robot.Robot(100, 0, pathfinding.NodePos(4, 4, 0))
# scene.addItem(bot1)
# scene.addItem(bot2)

# a = 0
# for c in cells:
#     r = QGraphicsRectItem(c[0]*100, c[1]*100, 100, 100)
#     r.setBrush(colors[a])
#     scene.addItem(r)
#     a += 1

# view.setScene(scene)

# mainwindow.setCentralWidget(view)

# mainwindow.show()
# sys.exit(app.exec())
