import random
import threading
import time

import networkx as nx

from aco_routing import random_ant, routing_ant, minority_ant
from aco_routing.wave_config import WaveConfig
from aco_routing.graph_tools import GraphTools


class AntColonyRunner:
    """
    Driver fot the ant colony. Runs itself in a separate thread
    """

    G: nx.DiGraph                           # the graph

    ants: list[random_ant.Random_Ant] = []  # list of currently stepping (alive) ants
    iteration: int                          # number of the current iteration
    waves: list[WaveConfig]                 # config for the current wave

    thread: threading.Thread                # thread object
    stop_event: threading.Event             # stop event

    def __init__(self, plot):
        self.plot = plot
        self.G = plot.G
        self.stop_event = threading.Event()

        self.waves = []
        for wave in plot.ants_config:
            self.waves.append(WaveConfig(wave))

    def start(self):
        """
        starts _run() in a separate thread
        """

        self.thread = threading.Thread(target=self._run)
        self.stop_event = threading.Event()
        self.thread.start()

    def stop(self):
        """
        stops the current thread
        """

        self.stop_event.set()

    def evaporation(self, rate: float):
        """
        reduces all pheromones by a given factor

        :param rate: reducing factor
        """

        for u, v, data in self.G.edges(data=True):
            self.G[u][v]['pheromone'] *= (1 - rate)

    def spawn_ant(self, wave):
        """
        creates an ant object depending on a given class

        :param wave: a wave object
        :return: an ant object
        """

        if wave.ant_class == "random":
            return random_ant.Random_Ant(self.G, wave)
        if wave.ant_class == "routing":
            return routing_ant.RoutingAnt(self.G, wave)
        if wave.ant_class == "minority":
            return minority_ant.MinorityAnt(self.G, wave)

    def _change_graph_values(self, wave):
        """
        Changes node values for a new wave

        :param wave: a wave-object
        """

        for change in wave.node_value_changes:
            nx.set_node_attributes(self.G, {change: {'value': wave.node_value_changes[change]}})

    def _count_pheromoned_edges(self) -> int:
        """
        counts pheromoned edges to check which are visited

        :return: number of pheromones edges
        """

        total_edges: int = len(self.G.edges.keys())
        pheromoned_edges: int = 0
        edges = self.G.edges(data=True)
        for i, o, data in edges:
            if data['pheromone'] > 0:
                pheromoned_edges += 1

        return pheromoned_edges

    def _remove_edges(self, wave):
        """
        Removes a list of edges

        :param wave: a wave-object
        """

        for tail, head in wave.remove_edges:
            GraphTools.delete_edge(self.G, tail, head, self.plot.pos)

    def _run(self):
        """
        controls the steps of the ants, runs iterations of stepping ants and runs waves of iterations
        """

        time.sleep(1)

        """
        a wave is a configuration of ants.
        with waves it it possible to configure different groups of iterations.
        It can be useful for elite ants or combining different ant types in one experiment
        """
        for wave in self.waves:
            if self.stop_event.is_set():
                break

            self._change_graph_values(wave)
            self._remove_edges(wave)

            '''
            iterations define a number of ants, which can walk at the same time and which behave homogeneous
            '''
            for iteration in range(wave.max_iterations):
                if self.stop_event.is_set():
                    break

                # spawn ants
                self.ants.clear()
                for i in range(0, wave.concurrent_ants):
                    if wave.ant_random_spawn:
                        wave.ant_spawn_node = random.choice(list(self.G.nodes()))
                    self.ants.append(self.spawn_ant(wave))

                # Evaporate pheromones after each iteration
                self.evaporation(wave.evaporation_rate)

                '''
                steps are the steps of the ants. passing one edge at a time.
                '''
                for steps in range(wave.ant_max_steps):
                    if self.stop_event.is_set():
                        break

                    # delete an ant from the list of this iteration if it stops stepping
                    for i, ant in enumerate(self.ants):
                        if not ant.step():  # Each ant performs one step and dies if not
                            self.ants.pop(i)

                    if len(self.ants) > 0:
                        time.sleep(wave.step_sleep)

                time.sleep(wave.iteration_sleep)
                print("Edges found so far: " + str(self._count_pheromoned_edges()))

            time.sleep(wave.wave_sleep)

        print("Run finished")

        self.stop()
