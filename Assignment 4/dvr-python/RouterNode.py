#!/usr/bin/env python
from typing import List
from RouterSimulator import RouterSimulator
from GuiTextArea import GuiTextArea
from RouterPacket import RouterPacket
from copy import deepcopy
from F import F

INFTY: int
N: int


class RouterNode:
    ID: int
    myGUI: GuiTextArea
    sim: RouterSimulator

    costs: List[int]
    neighbors: List[int]
    routes: List[int]
    distances: List[List[int]]

    def __init__(self, ID: int, sim: RouterSimulator, costs: List[int]):
        self.ID = ID
        self.sim = sim
        self.myGUI = GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        # Setup constants
        global N, INFTY
        N = sim.NUM_NODES
        INFTY = sim.INFINITY

        # Setup costs
        self.costs = deepcopy(costs)

        # Setup neighbors
        self.neighbors = [y for y in range(N) if costs[y] != INFTY and y != ID]

        # Setup routes for neighbors
        self.routes = [y if y in self.neighbors else -1 for y in range(N)]
        self.routes[ID] = ID

        # Setup distance matrix
        self.distances = [[INFTY for m in range(N)] for n in range(N)]
        self.distances[ID] = deepcopy(costs)

        # Send first update
        self.sendUpdates()

    # Updates our distance vector and informs our neighbors if it changes
    def update(self):
        changed = False
        # For every node y
        for y in range(N):
            if y == self.ID:
                continue

            min_cost = INFTY
            min_route = -1
            # Test all neighbors for better routes
            for v in self.neighbors:
                # Cost is going from neighbor to y and from us to neighbor
                cost = self.costs[v] + self.distances[v][y]
                if cost < min_cost:
                    min_cost = cost
                    min_route = v

            # If we found a new minimal cost or the route changed
            if self.distances[self.ID][y] != min_cost or self.routes[y] != min_route:
                self.distances[self.ID][y] = min_cost
                self.routes[y] = min_route
                changed = True

        # If one or more entries in our distance vector changed
        if changed:
            self.sendUpdates()

    # On receiving an updated distance vector from a neighbor
    def recvUpdate(self, pkt):
        self.myGUI.println(
            f"[Router {self.ID}] Received distance vector from Router {pkt.sourceid}"
        )
        # Set new distance vector and see if we can update
        self.distances[pkt.sourceid] = pkt.mincost
        self.update()

    def updateLinkCost(self, dest, newcost):
        self.myGUI.println(
            f"[Router {self.ID}] Received link cost update to destination {dest}: old({self.costs[dest]}), new({newcost})"
        )

        # Set new link cost and update
        self.costs[dest] = newcost
        self.update()

    def printDistanceTable(self):
        self.myGUI.println(f"Routing table for {self.ID} at {self.sim.getClocktime()}")
        self.myGUI.println('_'* 40 )        
        self.myGUI.println(f'{F.format("",10)} | {F.format("0", 5) } | {F.format("1", 5) } | {F.format("2", 5) } | ' )           
        self.myGUI.println('_'* 40 )

        for n in range(N):
            self.myGUI.print(f'{F.format(n,10)} | ')
            for m in range(N):
                self.myGUI.print(f"{F.format(self.distances[n][m],5)} | ")

            self.myGUI.println("")

        
        self.myGUI.println('_'* 40 )


        self.myGUI.println(f'{F.format("Costs",10)} | {F.format(self.distances[self.ID][0], 5) } | {F.format(self.distances[self.ID][1], 5) } | {F.format(self.distances[self.ID][2], 5) } | ' )
        self.myGUI.println(f'{F.format("Routes",10)} | {F.format(self.routes[0], 5) } | {F.format(self.routes[1], 5) } | {F.format(self.routes[2], 5) } | ' )

        
   
        self.myGUI.println('_'* 40 )
        self.myGUI.println('_'* 40 )

    # Sends our updated distance vector to all neighbors
    def sendUpdates(self):
        for v in self.neighbors:
            distance_vector = deepcopy(self.distances[self.ID])

            # If poison reverse was enabled, set the cost of routes going through neighbor v to INFTY
            if self.sim.POISONREVERSE:
                # For every node y
                for y in range(N):
                    # Set to infty if we are going through v for y, but v is not the goal node
                    if self.routes[y] == v and y != v:
                        distance_vector[y] = INFTY

            self.myGUI.println(
                f"[Router {self.ID}] Sent my distance vector {distance_vector} to Router {v}"
            )
            self.sim.toLayer2(RouterPacket(self.ID, v, distance_vector))