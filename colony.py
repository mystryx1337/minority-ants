import threading
import time
import random
import networkx as nx
from typing import List, Tuple

import minority_ant

'''
Inspiration Source: https://github.com/hasnainroopawalla/Ant-Colony-Optimization/blob/master/aco_routing/aco.py
'''

class AntColonyRunner():
    G: nx.DiGraph
    thread: threading.Thread

    # Maximum number of steps an ant is allowed is to take in order to reach the destination
    ant_max_steps: int

    # Number of cycles/waves of search ants to be deployed
    num_iterations: int

    # Indicates if the search ants should spawn at random nodes in the graph
    ant_random_spawn: bool = True

    # Evaporation rate (rho)
    evaporation_rate: float = 0.1

    # Pheromone bias
    alpha: float = 0.7

    # Edge cost bias
    beta: float = 0.3

    # Search ants
    #search_ants: List[Ant] = field(default_factory=list)

    def __init__(self, G, plot):
        self.G = G
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()
        self.plot = plot

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        ant = minority_ant.Minority_Ant(self.G,"S")
        time.sleep(2)
        while not self.stop_event.is_set():
            ant.step()

            self.plot.update_plot()
            time.sleep(2)