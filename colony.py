import threading
import time
import random
import networkx as nx
from typing import List

import minority_ant
import random_ant
import routing_ant

'''
Inspiration Source: https://github.com/hasnainroopawalla/Ant-Colony-Optimization/blob/master/aco_routing/aco.py
'''


class AntColonyRunner():
    G: nx.DiGraph
    ants: List[random_ant.Random_Ant] = []
    iteration: int

    # Maximum number of steps an ant is allowed is to take in order to reach the destination
    ant_max_steps: int = 20

    # Number of cycles/waves of search ants to be deployed
    max_iterations: int = 15

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

    # Pick a random edge by chance
    random_chance: float = 0.05

    # Search ants
    number_of_ants: int = 1

    # type of ant: random | routing | minority
    ant_class: str = "routing"

    def __init__(self, G, plot):
        self.G = G
        self.stop_event = threading.Event()
        self.plot = plot

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def evaporation(self):
        for u, v, data in self.G.edges(data=True):
            self.G[u][v]['pheromone'] *= (1 - self.evaporation_rate)

    def spawn_ant(self):
        if self.ant_class == "random":
            return random_ant.Random_Ant(self.G, self.ant_spawn_node, alpha=self.alpha, beta=self.beta,
                                         max_steps=self.ant_max_steps)
        if self.ant_class == "routing":
            return routing_ant.Routing_Ant(self.G, self.ant_spawn_node, alpha=self.alpha, beta=self.beta,
                                           max_steps=self.ant_max_steps, random_chance=self.random_chance)
        if self.ant_class == "minority":
            return minority_ant.Minority_Ant(self.G, self.ant_spawn_node, alpha=self.alpha, beta=self.beta,
                                             max_steps=self.ant_max_steps, random_chance=self.random_chance)

    def _run(self):
        # spawn ants
        for i in range(0, self.number_of_ants):
            if self.ant_random_spawn:
                self.ant_spawn_node = random.choice(list(self.G.nodes()))
            self.ants.append(self.spawn_ant())

        time.sleep(2)
        self.iteration = 0
        active_ants = self.number_of_ants

        while not self.stop_event.is_set() and self.iteration <= self.max_iterations:

            self.evaporation()

            for ant in self.ants:
                print(" start " + ant.start_node + " curr " + ant.current_node + " path " + str(ant.path))
                if not ant.step():  # Each ant performs one step
                    active_ants -= 1  # If the ant is finished, reduce the count
                    print(active_ants)

            if not self.plot.status['ants_running']:
                self.plot.status['ants_running'] = True

            if active_ants <= 0:
                break  # Exit if all ants are done

            time.sleep(1)
            self.iteration += 1

        self.stop()
