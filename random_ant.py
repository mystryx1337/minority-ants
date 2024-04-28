import networkx as nx
import random
from typing import List

class Random_Ant:
    G: nx.DiGraph           # the graph, on which the ant is walking
    start_node: str         # start node on the graph
    current_node: str       # current node

    alpha: float            # how much influence trail has
    beta: float             # how much influence attractiveness has

    success: bool = False   # does the ant put pheromones on its way

    max_steps: int          # how many steps can the ant do before giving up
    path: List[str] = []    # Path taken by the ant so far
    path_cost: float = 0.0  # Cost of the path taken by the ant so far

    def __init__(self, G: nx.DiGraph, start_node: str, alpha=1, beta=1, max_steps=20):
        # set Parameters
        self.G = G
        self.alpha = alpha
        self.beta = beta
        self.max_steps = max_steps
        self.start_node = start_node

        # Spawn
        self.current_node = start_node
        self.path.append(start_node)

    def _probability_for_node(self, target_node: str) -> float:
        data = self.G[self.current_node][target_node]
        alpha = self.alpha
        beta = self.beta
        tau = data["pheromone"]
        weight = data["weight"]
        eta = 1 #TODO: 1/d mit d= Distanz zum Knoten
        allowed_nodes_sum = 1 #TODO

        return ( (tau ** alpha) * (eta ** beta) ) / allowed_nodes_sum

    def _pick_a_new_node(self) -> str:
        unvisited_neighbors = self._get_unvisited_neighbors()
        if len(unvisited_neighbors) > 0:
            return random.choices(self._get_unvisited_neighbors())[0]
        return self.current_node

    def _get_unvisited_neighbors(self) -> List[str]:
        possible_edges = self.G.edges([self.current_node], data=True)
        unvisited_neighbors = []
        for current_node, possible_target, data in possible_edges:
            if possible_target not in self.path:
                unvisited_neighbors.append(possible_target)
        return unvisited_neighbors

    def _check_success(self):
        if self.G.nodes[self.current_node]['value'] > 0:
            self.success = True

    def _increase_pheromone(self, new_node):
        # Check if both nodes and the edge between them exist
        if new_node in self.G[self.current_node]:
            current_pheromones = self.G[self.current_node][new_node]['pheromone']
            self.G[self.current_node][new_node].update({'pheromone': current_pheromones + 1})
        else:
            # Error when the node or edge does not exist
            print(f"No such edge: {self.current_node} -> {new_node}")

    def step(self):
        if (self.current_node != self.start_node or not self.success) and len(self.path) < self.max_steps:
            new_node = self._pick_a_new_node()
            self.path.append(new_node)
            self._check_success()

            # If on a Path for Success:
            if self.success:
                self._increase_pheromone(new_node)

            self.current_node = new_node
            return True
        return False

    # def run(self):
    #     #Do steps, till it is successful and back
    #     # while (self.current_node != self.start_node or not self.success) and len(self.path) < self.max_steps:
    #     self._step()
