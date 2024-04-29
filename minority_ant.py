import routing_ant
import numpy as np
import random


class Minority_Ant(routing_ant.Routing_Ant):
    def _value_for_node(self, target_node) -> float:
        return super()._value_for_node(target_node)

    def _pick_a_new_node(self) -> str:
        node_values = self._get_all_possible_nodes_value()
        node_probabilities = np.divide(node_values,np.sum(node_values))
        return random.choices(target_nodes, weights=node_probabilities, k=1)[0]
