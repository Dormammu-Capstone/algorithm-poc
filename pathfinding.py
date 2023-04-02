from __future__ import annotations

import heapq
from enum import IntEnum

from PySide6.QtCore import QPoint


class Direction(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3


# class that have only x,y


# is it necessary nodepos and viewpos are child of pos?
# maybe what we need is just node (x,y)
class Pos:
    def __init__(self, x, y, direction) -> None:
        self.x: int = int(x)
        self.y: int = int(y)
        self.direction: int = int(direction)

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y and self.direction == __o.direction

    def __hash__(self) -> int:
        return hash("x%dy%dd%d" % (self.x, self.y, self.direction))

    def __repr__(self) -> str:
        return "x:%d y:%d dir:%d" % (self.x, self.y, self.direction)

    def point(self):
        return QPoint(self.x, self.y)

    def degree(self):
        return self.direction*90


class ViewPos(Pos):
    def __init__(self, x, y, direction) -> None:
        super().__init__(x, y, direction)

    def toNodePos(self) -> NodePos:
        return NodePos(self.x//100, self.y//100, self.direction)

    def __eq__(self, __o: object) -> bool:
        return type(__o) is ViewPos and super().__eq__(__o)

    def __hash__(self) -> int:
        return super().__hash__()


class NodePos(Pos):
    def __init__(self, x, y, direction) -> None:
        super().__init__(x, y, direction)

    def toViewPos(self) -> ViewPos:
        return ViewPos(self.x*100, self.y*100, self.direction)

    def __eq__(self, __o: object) -> bool:
        return type(__o) is NodePos and super().__eq__(__o)

    def __hash__(self) -> int:
        return super().__hash__()

    def __lt__(self, __o: object) -> bool:
        return True


def facingEach(a: NodePos, b: NodePos):
    return (a.direction+b.direction) % 2 == 0


graphx = 0
graphy = 0
cells = {}


def registerMap(icells, grid):
    global graphx
    global graphy
    global cells
    cells = icells
    graphx = grid[0]
    graphy = grid[1]


def generateGraph(tempBlocked: list[tuple[int, int]] = []):
    nodes = [(i, j) for j in range(graphx) for i in range(graphy)]
    edges: dict[NodePos, list[tuple[NodePos, int]]] = {}
    orientedNodes: list[NodePos] = []

    # fix nodes with map from db
    # for cells[blocked] nodes.remove

    for b in tempBlocked:
        nodes.remove(b)

    for n in nodes:
        for i in range(4):
            add = NodePos(n[0], n[1], i)
            orientedNodes.append(add)
            edges[add] = []

    for n in orientedNodes:
        # if data from file maybe addnode() may skip undescribed clockwise edges
        clockwise, counterwise = 0, 0
        if n.direction == 0:
            clockwise, counterwise = 1, 3
        elif n.direction == 3:
            clockwise, counterwise = 0, 2
        else:
            clockwise, counterwise = n.direction+1, n.direction-1
        edges[n].append((NodePos(n.x, n.y, clockwise), 10))
        edges[n].append((NodePos(n.x, n.y, counterwise), 10))

        # check adjacent cell/node
        # if data from file

        if n.direction == 0:
            if NodePos(n.x, n.y-1, n.direction) in orientedNodes:
                edges[n].append((NodePos(n.x, n.y-1, n.direction), 10))
        if n.direction == 1:
            if NodePos(n.x+1, n.y, n.direction) in orientedNodes:
                edges[n].append((NodePos(n.x+1, n.y, n.direction), 10))
        if n.direction == 2:
            if NodePos(n.x, n.y+1, n.direction) in orientedNodes:
                edges[n].append((NodePos(n.x, n.y+1, n.direction), 10))
        if n.direction == 3:
            if NodePos(n.x-1, n.y, n.direction) in orientedNodes:
                edges[n].append((NodePos(n.x-1, n.y, n.direction), 10))

    return orientedNodes, edges


def dijkstra(nodes: list[NodePos], edges: dict[NodePos, list[tuple[NodePos, int]]], src: NodePos):
    distances = {node: float('inf') for node in nodes}
    prevs: dict[NodePos, NodePos] = {node: None for node in nodes}
    queue: list[tuple[float, NodePos]] = []

    distances[src] = 0
    heapq.heappush(queue, (distances[src], src))

    while queue:
        currDist, currNode = heapq.heappop(queue)

        if distances[currNode] < currDist:
            # dont need to visit current_distance to current route
            # cuz current route is longer
            continue

        for neighbor, weight in edges[currNode]:
            alt = currDist + weight
            if alt < distances[neighbor]:
                distances[neighbor] = alt
                heapq.heappush(queue, (alt, neighbor))

                prevs[neighbor] = currNode

    return distances, prevs


def backTrack(prevs: dict[NodePos, NodePos], source: NodePos, destination: NodePos):
    route: list[NodePos] = [destination]

    currentTrace = destination
    while currentTrace != source:
        currentTrace = prevs[currentTrace]
        route.insert(0, currentTrace)
    return route


def evaluateRoute(src: NodePos, dest: NodePos, tempBlocked: list[tuple[int, int]] = []):
    nodes, edges = generateGraph(tempBlocked=tempBlocked)
    distances, prevs = dijkstra(nodes, edges, src)
    return backTrack(prevs, src, dest)


def evaluateRouteToCell(src: NodePos, dest: tuple[int, int]):
    nodes, edges = generateGraph()
    distances, prevs = dijkstra(nodes, edges, src)
    min = (None, float('inf'))
    for i in range(4):
        temp = NodePos(dest[0], dest[1], i)

        tempdist = distances[temp]
        if tempdist < min[1]:
            min = (temp, tempdist)

    return backTrack(prevs, src, min[0])
