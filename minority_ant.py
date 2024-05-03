import routing_ant
import numpy as np
import random


class Minority_Ant(routing_ant.Routing_Ant):
    def _value_for_node(self, target_node) -> float:
        return super()._value_for_node(target_node)

    def _pick_a_new_node(self) -> str:
        # random by chance
        if random.random() < self.random_chance:
            return super(routing_ant.Routing_Ant,self)._pick_a_new_node()

        # pheromone sensitive behaviour, if pheromones on its way
        node_values, target_nodes = self._get_all_unvisited_nodes_value()
        sum_node_values = np.sum(node_values)
        if(sum_node_values > 0):
            node_probabilities = (node_values / sum_node_values)
            node_probabilities = 1 - node_probabilities
            return random.choices(target_nodes, weights=node_probabilities, k=1)[0]

        # random otherwise
        return super(routing_ant.Routing_Ant,self)._pick_a_new_node()
