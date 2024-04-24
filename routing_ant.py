import networkx as nx
import random
import random_ant
from typing import List

class Routing_Ant(random_ant.Random_Ant):
    def _pick_a_new_node(self) -> str:
        possible_edges = self.G.edges([self.current_node], data=True)
        target_nodes = []
        probabilities = []
        for current_node, possible_target, data in possible_edges:
            pheromone = data["pheromone"]
            target_nodes.append(possible_target)

            probability_for_node = self._probability_for_node(possible_target)
            probabilities.append(probability_for_node)

        return random.choices(target_nodes, weights=probabilities, k=1)[0]