import networkx as nx
import plot


def add_edges_from_outgoing_node(G, outgoing_node, target_nodes, edge_weights=None, edge_pheromones=None, node_value=0):
    """
    Add edges from an outgoing node to a list of target nodes with optional edge weights.

    Parameters:
    - G: NetworkX graph object
    - outgoing_node: The node from which edges originate
    - target_nodes: List of nodes to which edges should be added
    - edge_weights: Optional list of edge weights corresponding to the edges being added
    """
    if len(target_nodes) == 0:
        return

    for i, target_node in enumerate(target_nodes):
        weight = 1
        if edge_weights is not None:
            weight = edge_weights[i]

        pheromone = 0.0
        if edge_pheromones is not None:
            pheromone = edge_pheromones[i]

        G.add_edge(outgoing_node, target_node, weight=weight, pheromone=pheromone)

    nx.set_node_attributes(G, {outgoing_node: {'value': node_value}})


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G = nx.DiGraph()

    # Kanten mit Gewichten und Pheromonen hinzufügen
    add_edges_from_outgoing_node(G, "A", ["B","D","E","S"])
    add_edges_from_outgoing_node(G, "B", ["A","C","D","E","F"])
    add_edges_from_outgoing_node(G, "C", ["B","E","F"], edge_weights=[3,3,3])
    add_edges_from_outgoing_node(G, "D", ["A","B","E","G","H","X"])
    add_edges_from_outgoing_node(G, "E", ["A","B","C","D","F","G","H"])
    add_edges_from_outgoing_node(G, "F", ["B","C","E","I"])
    add_edges_from_outgoing_node(G, "G", ["D","E","H","J","K"])
    add_edges_from_outgoing_node(G, "H", ["D","E","G","I","J","K","L"])
    add_edges_from_outgoing_node(G, "I", ["F","H","K","L"])
    add_edges_from_outgoing_node(G, "J", ["G","H","K"], edge_pheromones=[0.5, 0.8, 1.0])
    add_edges_from_outgoing_node(G, "K", ["G","H","I","J","L"])
    add_edges_from_outgoing_node(G, "L", ["H","I","K","Z"], edge_pheromones=[0.0, 0.0, 0.0, 1.0])
    add_edges_from_outgoing_node(G, "S", ["A"])
    add_edges_from_outgoing_node(G, "X", ["D"])
    add_edges_from_outgoing_node(G, "Z", ["L"], node_value=1)

    AcoPlotObj = plot.AcoPlot(G)
