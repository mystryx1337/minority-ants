import networkx as nx
import random

class Routing_Ant:
    G: nx.DiGraph
    current_node: str

    alpha: float    #how much influence trail has
    beta: float     #how much influence attractiveness has

    success: bool   #does the ant put pheromones on its way

    def __init__(self, G, start_node, alpha=1, beta=1):
        self.G = G
        self.current_node = start_node
        self.alpha = alpha
        self.beta = beta
        self.success = False

    def probability_for_node(self,target_node):
        data = self.G[self.current_node][target_node]
        alpha = self.alpha
        beta = self.beta
        tau = data["pheromone"]
        weight = data["weight"]
        eta = 1 #TODO: 1/d mit d= Distanz zum Knoten
        allowed_nodes_sum = 1 #TODO

        return ( (tau ** alpha) * (eta ** beta) ) / allowed_nodes_sum

    def pick_a_new_node(self):
        possible_edges = self.G.edges([self.current_node], data=True)
        target_nodes = []
        probabilities = []
        for current_node, possible_target, data in possible_edges:
            pheromone = data["pheromone"]
            target_nodes.append(possible_target)

            probability_for_node = self.probability_for_node(possible_target)
            probabilities.append(probability_for_node)

        return random.choices(target_nodes, weights=probabilities, k=1)[0]

    def increase_pheromone(self,new_node):
        current_pheromones = self.G[self.current_node][new_node]['pheromone']
        self.G[self.current_node][new_node].update({'pheromone': current_pheromones + 1})

    def step(self):
        new_node = self.pick_a_new_node()

        if self.success:
            self.increase_pheromone()

        self.current_node = new_node

    def run(self):
        #TODO: Do steps, till it is back
        pass



