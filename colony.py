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


class WaveConfig:
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
    concurrent_ants: int = 2

    # type of ant: random | routing | minority
    ant_class: str = "routing"

    # if the ant puts pheromones on its way or just backwards once on success
    put_pheromones_always: bool = False

    # if the ant dies at first success node
    stop_on_success: bool = True

    def __init__(self, wave):
        self.ant_class = wave['class'] if 'class' in wave else 'routing'
        self.ant_max_steps = wave['max_steps'] if 'max_steps' in wave else 20
        self.max_iterations = wave['max_iterations'] if 'max_iterations' in wave else 15
        self.ant_random_spawn = wave['random_spawn'] if 'random_spawn' in wave else False
        self.ant_spawn_node = wave['spawn_node'] if 'spawn_node' in wave else "S"
        self.evaporation_rate = wave['evaporation_rate'] if 'evaporation_rate' in wave else 0.1
        self.alpha = wave['alpha'] if 'alpha' in wave else 0.7
        self.beta = wave['beta'] if 'beta' in wave else 0.3
        self.random_chance = wave['random_chance'] if 'random_chance' in wave else 0.05
        self.concurrent_ants = wave['concurrent_ants'] if 'concurrent_ants' in wave else 2
        self.put_pheromones_always = wave['put_pheromones_always'] if 'put_pheromones_always' in wave else False
        self.stop_on_success = wave['stop_on_success'] if 'stop_on_success' in wave else True


class AntColonyRunner:
    G: nx.DiGraph
    ants: List[random_ant.Random_Ant] = []
    iteration: int
    waves: List[WaveConfig]

    def __init__(self, G, plot, ants_config):
        self.G = G
        self.plot = plot

        self.waves = []
        for wave in ants_config:
            self.waves.append(WaveConfig(wave))

    def start(self):
        print("Thread started")
        self.thread = threading.Thread(target=self._run)
        self.stop_event = threading.Event()
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def evaporation(self, rate: float):
        for u, v, data in self.G.edges(data=True):
            self.G[u][v]['pheromone'] *= (1 - rate)

    def spawn_ant(self, wave):
        if wave.ant_class == "random":
            return random_ant.Random_Ant(self.G, wave.ant_spawn_node, alpha=wave.alpha, beta=wave.beta,
                                         max_steps=wave.ant_max_steps)
        if wave.ant_class == "routing":
            return routing_ant.Routing_Ant(self.G, wave.ant_spawn_node, alpha=wave.alpha, beta=wave.beta,
                                           max_steps=wave.ant_max_steps, random_chance=wave.random_chance,
                                           put_pheromones_always=wave.put_pheromones_always,
                                           stop_on_success=wave.stop_on_success)
        if wave.ant_class == "minority":
            return minority_ant.Minority_Ant(self.G, wave.ant_spawn_node, alpha=wave.alpha, beta=wave.beta,
                                             max_steps=wave.ant_max_steps, random_chance=wave.random_chance,
                                             put_pheromones_always=wave.put_pheromones_always,
                                             stop_on_success=wave.stop_on_success)

    def _run(self):
        time.sleep(1)
        for wave in self.waves:
            for iteration in range(wave.max_iterations):
                # spawn ants
                self.ants.clear()
                for i in range(0, wave.concurrent_ants):
                    if wave.ant_random_spawn:
                        wave.ant_spawn_node = random.choice(list(self.G.nodes()))
                    self.ants.append(self.spawn_ant(wave))
    
                self.evaporation(wave.evaporation_rate)

                for steps in range(wave.ant_max_steps):
                    if self.stop_event.is_set():
                        self.stop()
                        
                    for i, ant in enumerate(self.ants):
                        print(" start " + ant.start_node + " curr " + ant.current_node + " path " + str(ant.path))
                        if not ant.step():  # Each ant performs one step
                            self.ants.pop(i)
                    
                    if len(self.ants) > 0:
                        time.sleep(1)

        self.stop()
