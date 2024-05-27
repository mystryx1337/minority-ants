import random
import random_ant
import numpy as np

class Routing_Ant(random_ant.Random_Ant):
    """
    The traditional routing ant
    """

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
        """
        changes the way of picking a new node compared to the random ant.
        This s the traditional routing ant.

        :return: new node
        """

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

    def _get_cost_of_current_path(self) -> int:
        """
        Calculates the cost of the current walked path

        :return: cost : int
        """

        cost: int = 0
        for i, current_node in enumerate(self.path):
            if i < len(self.path) - 1:
                next_node = self.path[i + 1]
                current_weight = self.G[current_node][next_node]['weight']
                cost += current_weight 
        return cost

    def _increase_pheromone_on_success(self):
        """
        Increases pheromones on the walked path only once after a successful walk.
        Absolute pheromones (double of maximum steps) are distributed to the edges to promote shorter paths
        """

        # when value node arrived: mark current path
        if self._check_success() and not self.put_pheromones_always:
            cost: int = self._get_cost_of_current_path()
            pheromones_to_put: float = self.max_steps / 2 / cost
            for i, current_node in enumerate(self.path):
                if i < len(self.path) - 1:
                    next_node = self.path[i + 1]

                    current_pheromones = self.G[current_node][next_node]['pheromone']
                    self.G[current_node][next_node].update({'pheromone': current_pheromones + pheromones_to_put})

    def _increase_pheromone(self, new_node):
        # when value node arrived: mark current path
        if self.put_pheromones_always:
            super()._increase_pheromone_always(new_node)
        else:
            self._increase_pheromone_on_success()
