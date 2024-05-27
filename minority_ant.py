import routing_ant
import numpy as np
import random
import networkx as nx


class Minority_Ant(routing_ant.Routing_Ant):
    """
    The minority ant: chooses with bigger probability an edge with lesser pheromones
    """

    def __init__(self, G: nx.DiGraph, wave):
        super().__init__(G, wave)

        self.prioritize_pheromone_routes = wave.prioritize_pheromone_routes

    def _pick_a_new_node(self) -> str:
        """
        choosing a new node.
        Variant 1: just calculation 1 - (probability of routing ant) -> search mechanism
        Variant 2: only choose from pheromoned edges -> load balancing mechanism

        :return: a new node
        """
        # random by chance
        if random.random() < self.random_chance:
            return super(routing_ant.Routing_Ant, self)._pick_a_new_node()

        # pheromone sensitive behaviour, if pheromones on its way
        edge_values, target_nodes = self._get_all_unvisited_nodes_value()

        # filter possible nodes for pheromones
        if self.prioritize_pheromone_routes:
            filtered_targets = []
            for i in range(edge_values.shape[0]):
                if edge_values[i] < 0.01:
                    filtered_targets.append(i)
            if len(filtered_targets) > 0:
                edge_values = np.delete(edge_values, filtered_targets)
                target_nodes = np.delete(target_nodes, filtered_targets)

        sum_edge_values = np.sum(edge_values)
        if sum_edge_values > 0:
            node_probabilities = 1 - (edge_values / sum_edge_values)

            if np.sum(node_probabilities) > 0:
                return random.choices(target_nodes, weights=node_probabilities, k=1)[0]
            else:
                return target_nodes[0]

        # random otherwise
        return super(routing_ant.Routing_Ant, self)._pick_a_new_node()
