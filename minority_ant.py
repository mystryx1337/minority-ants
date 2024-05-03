import routing_ant
import numpy as np
import random


class Minority_Ant(routing_ant.Routing_Ant):
    def _pick_a_new_node(self) -> str:
        # random by chance
        if random.random() < self.random_chance:
            return super(routing_ant.Routing_Ant, self)._pick_a_new_node()

        # pheromone sensitive behaviour, if pheromones on its way
        edge_values, target_nodes = self._get_all_unvisited_nodes_value()

        remove = []
        for i in range(edge_values.shape[0]):
            if edge_values[i] < 0.01:
                remove.append(i)
        if len(remove) > 0:
            edge_values = np.delete(edge_values, remove)
            target_nodes = np.delete(target_nodes, remove)

        sum_node_values = np.sum(edge_values)
        if sum_node_values > 0:
            node_probabilities = 1 - (edge_values / sum_node_values)

            if np.sum(node_probabilities) > 0:
                return random.choices(target_nodes, weights=node_probabilities, k=1)[0]

        # random otherwise
        return super(routing_ant.Routing_Ant, self)._pick_a_new_node()
