import networkx as nx

class Routing_Ant:
    G: nx.DiGraph
    current_node: str

    def __init__(self, G, start_node):
        self.G = G
        self.current_node = start_node

    def step(self):
        possible_edges = self.G.edges([self.current_node], data=True)
        for current_node, possible_target, data in possible_edges:
            print(possible_target)
            print(data)

            weight = data["weight"]
            pheromone = data["pheromone"]

        #self.G[self.current_node][possible_target].update({'weight': weight, 'pheromone': pheromone + 0.5})


