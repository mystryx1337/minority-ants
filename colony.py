import threading
import time
import random
import networkx as nx
from typing import List

import minority_ant

'''
Inspiration Source: https://github.com/hasnainroopawalla/Ant-Colony-Optimization/blob/master/aco_routing/aco.py
'''

class AntColonyRunner():
    G: nx.DiGraph
    thread: threading.Thread
    ants: List = []
    iteration: int

    # Maximum number of steps an ant is allowed is to take in order to reach the destination
    ant_max_steps: int = 20

    # Number of cycles/waves of search ants to be deployed
    num_iterations: int = 10

    # Indicates if the search ants should spawn at random nodes in the graph
    ant_random_spawn: bool = False

    # Sets a manual start node, if it is not random
    ant_spawn_node: str = "S"

    # Evaporation rate (rho)
    evaporation_rate: float = 0.1

    # Pheromone bias
    alpha: float = 0.7

    # Edge cost bias
    beta: float = 0.3

    # Search ants
    number_of_ants: int = 1

    def __init__(self, G, plot):
        self.G = G
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()
        self.plot = plot

        if self.ant_random_spawn:
            self.ant_spawn_node = random.choice(list(G.nodes()))

        for i in range(0,self.number_of_ants):
            self.ants.append(minority_ant.Minority_Ant(self.G,self.ant_spawn_node, alpha=self.alpha, beta=self.beta, max_steps=self.ant_max_steps))

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def evaporation(self):
        for u, v, data in self.G.edges(data=True):
            self.G[u][v]['pheromone'] *= (1-self.evaporation_rate)

    def run(self):
        time.sleep(2)
        self.iteration = 0
        while not self.stop_event.is_set() and self.num_iterations < self.iteration:
            #TODO: Show on Plot, which iteration we are in

            self.evaporation()

            for ant in self.ants:
                ant.run()

            self.plot.update_plot()
            time.sleep(2)

        self.stop()