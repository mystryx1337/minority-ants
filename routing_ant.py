import random
import random_ant
import numpy as np

class Routing_Ant(random_ant.Random_Ant):
    def _get_all_unvisited_nodes_value(self) -> tuple[np.ndarray[np.dtype[float], np.dtype[float]], np.ndarray[np.dtype[str], np.dtype[str]]]:
        possible_edges = self.G.edges([self.current_node], data=True)
        target_nodes = np.array([])
        node_values = np.array([])
        for current_node, possible_target, data in possible_edges:
            if possible_target not in self.path:
                target_nodes = np.append(target_nodes, possible_target)

                node_value = self._value_for_node(possible_target)
                node_values = np.append(node_values, node_value)
        return node_values, target_nodes

    def _pick_a_new_node(self) -> str:
        # random by chance
        if random.random() < self.random_chance:
            return super()._pick_a_new_node()

        # pheromone sensitive behaviour, if pheromones on its way
        node_values, target_nodes = self._get_all_unvisited_nodes_value()
        sum_node_values = np.sum(node_values)
        if(sum_node_values > 0):
            node_probabilities = (node_values / sum_node_values)
            return random.choices(target_nodes, weights=node_probabilities, k=1)[0]

        # random otherwise
        return super()._pick_a_new_node()

    def _increase_pheromone(self, new_node):
        # when value node arrived: mark current path
        if self._check_success() and not self.put_pheromones_always:
            print("put pheromones!")
            for i, current_node in enumerate(self.path):
                if i < len(self.path) - 1:
                    next_node = self.path[i + 1]

                    current_pheromones = self.G[current_node][next_node]['pheromone']
                    self.G[current_node][next_node].update({'pheromone': current_pheromones + 1})
