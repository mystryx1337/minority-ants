import threading
import time
import random
import networkx as nx

import minority_ant
import random_ant
import routing_ant
from graph_tools import GraphTools

'''
Inspiration Source: https://github.com/hasnainroopawalla/Ant-Colony-Optimization/blob/master/aco_routing/aco.py
'''


class WaveConfig:
    """
    encapsulates all parameters for a wave in an object
    """

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

    # Minority Ant: If weakest trace should be selected only from traces edges
    prioritize_pheromone_routes: bool = False

    # Sleep times for different loops
    step_sleep: float = 0.5
    iteration_sleep: float = 0.5
    wave_sleep: float = 0.5

    # change graph values for this wave
    node_value_changes: dict

    # remove edges
    remove_edges: list[list[str]]

    def __init__(self, wave: dict):
        self.ant_class = wave.get('class', 'routing')
        self.ant_max_steps = wave.get('ant_max_steps', 20)
        self.max_iterations = wave.get('max_iterations', 15)
        self.ant_random_spawn = wave.get('random_spawn', False)
        self.ant_spawn_node = wave.get('spawn_node', "AU")
        self.evaporation_rate = wave.get('evaporation_rate', 0.1)
        self.alpha = wave.get('alpha', 0.7)
        self.beta = wave.get('beta', 0.3)
        self.random_chance = wave.get('random_chance', 0.05)
        self.concurrent_ants = wave.get('concurrent_ants', 2)
        self.put_pheromones_always = wave.get('put_pheromones_always', False)
        self.stop_on_success = wave.get('stop_on_success', True)
        self.prioritize_pheromone_routes = wave.get('prioritize_pheromone_routes', False)

        self.step_sleep = wave.get('step_sleep', 0.5)
        self.iteration_sleep = wave.get('iteration_sleep', 0.5)
        self.wave_sleep = wave.get('wave_sleep', 0.5)

        self.node_value_changes = wave.get('node_value_changes', {})
        self.remove_edges = wave.get('remove_edges', [])

    def to_dict(self):
        return {
            'class': self.ant_class,
            'ant_max_steps': self.ant_max_steps,
            'max_iterations': self.max_iterations,
            'random_spawn': self.ant_random_spawn,
            'spawn_node': self.ant_spawn_node,
            'evaporation_rate': self.evaporation_rate,
            'alpha': self.alpha,
            'beta': self.beta,
            'random_chance': self.random_chance,
            'concurrent_ants': self.concurrent_ants,
            'put_pheromones_always': self.put_pheromones_always,
            'stop_on_success': self.stop_on_success,
            'prioritize_pheromone_routes': self.prioritize_pheromone_routes,
            'step_sleep': self.step_sleep,
            'iteration_sleep': self.iteration_sleep,
            'wave_sleep': self.wave_sleep,
            'node_value_changes': self.node_value_changes,
            'remove_edges': self.remove_edges
        }


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
            return routing_ant.Routing_Ant(self.G, wave)
        if wave.ant_class == "minority":
            return minority_ant.Minority_Ant(self.G, wave)

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

        '''
        a wave is a configuration of ants.
        with waves it it possible to configure different groups of iterations.
        It can be useful for elite ants or combining different ant types in one experiment
        '''
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
