import heapq
from enum import Enum, IntEnum

# todo: create class to edge/node and robot operation queue

cached = False
nodes = None
edges = None


class Direction(IntEnum):
    N = 1
    E = 2
    S = 3
    W = 4
# todo: fix duplicates
# currently, generate all path include duplicates

# src-dest-dist-startori-destori
# ewns 4 directions required

# todo: get graph from database as argument


def generateGraph():
    # working: 4 directions
    def addEdge(edges, primitiveSrc, primitiveDest, direction):
        orientedNode = (*primitiveSrc, direction)
        if orientedNode not in edges:
            edges[orientedNode] = []

        edges[orientedNode].append(
            ((*primitiveDest, direction), 1000))

    length = 5
    nodes = [(i, j) for j in range(length) for i in range(length)]
    edges = {}
    orientedNodes = []

    for node in nodes:
        # changed direction v,h to nsew
        # this mean that robot can face north in 0,0
        # this is different from v,h system
        # that there is no 0,0 cell facing north
        #  ||
        # -00-
        # -00-
        #  ||
        # todo: after get map from database, check this cell is good to go
        if (node[0]-1, node[1]) in nodes:
            addEdge(edges, node, (node[0]-1, node[1]), Direction.W)
            orientedNodes.append((*node, Direction.W))
        if (node[0]+1, node[1]) in nodes:
            addEdge(edges, node, (node[0]+1, node[1]), Direction.E)
            orientedNodes.append((*node, Direction.E))
        if (node[0], node[1]-1) in nodes:
            addEdge(edges, node, (node[0], node[1]-1), Direction.N)
            orientedNodes.append((*node, Direction.N))
        if (node[0], node[1]+1) in nodes:
            addEdge(edges, node, (node[0], node[1]+1), Direction.S)
            orientedNodes.append((*node, Direction.S))

        # assume all cells are intersection to 4 direction
        # todo: determine cell is intersection 4, intersection 3, straight, corner
        enode = (*node, Direction.E)
        wnode = (*node, Direction.W)
        snode = (*node, Direction.S)
        nnode = (*node, Direction.N)

        orientedNodes.append(enode)
        orientedNodes.append(wnode)
        orientedNodes.append(snode)
        orientedNodes.append(nnode)

        if enode not in edges:
            edges[enode] = []
        if wnode not in edges:
            edges[wnode] = []
        if snode not in edges:
            edges[snode] = []
        if nnode not in edges:
            edges[nnode] = []

        if enode in orientedNodes:
            if snode in orientedNodes:
                edges[enode].append((snode, 1000))
            if nnode in orientedNodes:
                edges[enode].append((nnode, 1000))
        if wnode in orientedNodes:
            if snode in orientedNodes:
                edges[wnode].append((snode, 1000))
            if nnode in orientedNodes:
                edges[wnode].append((nnode, 1000))
        if snode in orientedNodes:
            if enode in orientedNodes:
                edges[snode].append((enode, 1000))
            if wnode in orientedNodes:
                edges[snode].append((wnode, 1000))
        if nnode in orientedNodes:
            if enode in orientedNodes:
                edges[nnode].append((enode, 1000))
            if wnode in orientedNodes:
                edges[nnode].append((wnode, 1000))

        # if ew and ns:
        #     edges[hnode].append((vnode, 1000))
        #     edges[vnode].append((hnode, 1000))

    return orientedNodes, edges


def dijkstra(nodes, edges, source):
    distances = {node: float('inf') for node in nodes}
    distances[source] = 0

    prevs = {node: None for node in nodes}

    queue = []
    heapq.heappush(queue, (distances[source], source))

    while queue:
        currentDistance, currentNode = heapq.heappop(queue)
        if distances[currentNode] < currentDistance:
            # dont need to visit current_distance to current route
            # cuz current route is longer
            continue

        for neighbor, weight in edges[currentNode]:
            alt = currentDistance + weight
            if alt < distances[neighbor]:
                distances[neighbor] = alt
                heapq.heappush(queue, (alt, neighbor))

                prevs[neighbor] = currentNode

    return distances, prevs


def findRoute(prevs, source, destination):
    route = [destination]

    currentTrace = destination
    while currentTrace != source:
        currentTrace = prevs[currentTrace]
        route.insert(0, currentTrace)
    return route


def getGraph():
    if not cached:
        nodes, edges = generateGraph()
    return nodes, edges
