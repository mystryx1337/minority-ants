import networkx as nx
import plot
import json


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


def load_config_from_json():
    G = nx.DiGraph()

    # Opening JSON file
    f = open('configurations/test.json')

    data: dict = json.load(f)

    f.close()

    for node in data['nodes']:
        target_nodes: list[str] = data['nodes'][node]['edges']
        edge_weights: list[int] = data['nodes'][node]['weights'] if 'weights' in data['nodes'][node] else None
        pheromones: list[float] = data['nodes'][node]['pheromones'] if 'pheromones' in data['nodes'][node] else None
        node_value: int = data['nodes'][node]['value'] if 'value' in data['nodes'][node] else 0
        add_edges_from_outgoing_node(G, node, target_nodes, edge_weights=edge_weights, edge_pheromones=pheromones,
                                     node_value=node_value)

    ants: list = data['ants']

    return G, ants


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    G, ants = load_config_from_json()

    AcoPlotObj = plot.AcoPlot(G, ants)
