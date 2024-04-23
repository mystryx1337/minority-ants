import networkx as nx

class Routing_Ant:
    G: nx.DiGraph
    current_node: str

    def __init__(self, G, start_node):
        self.G = G
        self.current_node = start_node

    def step(self):
        possible_edges = self.G.edges([self.current_node], data=True)
        print(possible_edges[0])

        #possible_target = possible_edges[0][1]
        #weight = self.G[self.current_node][possible_target]["weight"]
        #pheromone = self.G[self.current_node][possible_target]["pheromone"]

        #self.G[self.current_node][possible_target].update({'weight': weight, 'pheromone': pheromone + 0.5})


