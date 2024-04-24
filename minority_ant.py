import routing_ant

class Minority_Ant(routing_ant.Routing_Ant):
    def _probability_for_node(self, target_node) -> float:
        return super()._probability_for_node(target_node)
