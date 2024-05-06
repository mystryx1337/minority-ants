import json
import string
import networkx as nx
import numpy as np


class GraphTools:
    @staticmethod
    def load_config_from_json():
        G = nx.DiGraph()

        # Opening JSON file
        f = open('configurations/minority_traffic_graph.json')

        data: dict = json.load(f)

        f.close()

        if 'macro' in data['nodes']:
            if data['nodes']['macro']['type'] == 'fully_linked_graph':
                nodes = GraphTools.generate_nodes(data['nodes']['macro']['x'])
                for node in nodes:
                    exclusive_nodes = nodes.copy()
                    exclusive_nodes.remove(node)
                    GraphTools.add_edges_from_outgoing_node(G, node, exclusive_nodes)
            if data['nodes']['macro']['type'] == '2d_grid_torus':
                x: int = data['nodes']['macro']['x']
                y: int = data['nodes']['macro']['y']
                nodes = GraphTools.generate_nodes(x * y)
                nodes_2d = np.array(nodes).reshape(x, y)
                for i in range(x):
                    for j in range(y):
                        node = nodes_2d[i, j]
                        neighborhood_nodes = [
                            nodes_2d[(i - 1) % x, j],
                            nodes_2d[(i + 1) % x, j],
                            nodes_2d[i, (j + 1) % y],
                            nodes_2d[i, (j - 1) % y]]
                        GraphTools.add_edges_from_outgoing_node(G, node, neighborhood_nodes)
            if data['nodes']['macro']['type'] == 'small_world':
                pass
            
        for node in data['nodes']:
            if node != 'macro':
                target_nodes: list[str] = data['nodes'][node]['edges'] if 'edges' in data['nodes'][node] else []
                edge_weights: list[int] = data['nodes'][node]['weights'] if 'weights' in data['nodes'][node] else None
                pheromones: list[float] = data['nodes'][node]['pheromones'] if 'pheromones' in data['nodes'][node] else None
                node_value: int = data['nodes'][node]['value'] if 'value' in data['nodes'][node] else 0
                GraphTools.add_edges_from_outgoing_node(G, node, target_nodes, edge_weights=edge_weights,
                                                        edge_pheromones=pheromones, node_value=node_value)

        if not 'ants' in data:
            data['ants'] = {}

        if not 'plot' in data:
            data['plot'] = {}

        return G, data['ants'], data['plot']

    @staticmethod
    def generate_nodes(n: int):
        alphabet = list(string.ascii_uppercase)
        if n <= 26:
            return alphabet[0:n]
        else:
            double_alphabet = [letter1 + letter2 for letter1 in alphabet for letter2 in alphabet]
            return double_alphabet[0:n]

    @staticmethod
    def add_edges_from_outgoing_node(G: nx.DiGraph, outgoing_node: str, target_nodes: list[str], edge_weights=None, edge_pheromones=None,
                                     node_value=0):
        """
        Add edges from an outgoing node to a list of target nodes with optional edge weights.

        Parameters:
        - G: NetworkX graph object
        - outgoing_node: The node from which edges originate
        - target_nodes: List of nodes to which edges should be added
        - edge_weights: Optional list of edge weights corresponding to the edges being added
        """
        if len(target_nodes) > 0:
            for i, target_node in enumerate(target_nodes):
                weight = 1
                if edge_weights is not None:
                    weight = edge_weights[i]
    
                pheromone = 0.0
                if edge_pheromones is not None:
                    pheromone = edge_pheromones[i]
    
                G.add_edge(outgoing_node, target_node, weight=weight, pheromone=pheromone)

        nx.set_node_attributes(G, {outgoing_node: {'value': node_value}})

    @staticmethod
    def add_edge(G, tail, head, weight, tail_value=None, head_value=None):
        try:
            weight = float(weight)
        except ValueError:
            weight = 1.0  # Set default weight if conversion fails

        # Change node value
        if tail == '' and head != '':
            GraphTools.change_node_value(G, head, weight)
            return
        if tail != '' and head == '':
            GraphTools.change_node_value(G, tail, weight)
            return

        # Add or update nodes with the specified or default 'value'
        if not G.has_node(tail):
            G.add_node(tail, value=tail_value if tail_value is not None else 0)  # Set a default or specified value
        else:
            if tail_value is not None:
                G.nodes[tail]['value'] = tail_value  # Update the value if specified

        if not G.has_node(head):
            G.add_node(head, value=head_value if head_value is not None else 0)  # Set a default or specified value
        else:
            if head_value is not None:
                G.nodes[head]['value'] = head_value  # Update the value if specified

        # Add the edge with weight and pheromone
        G.add_edge(tail, head, weight=weight, pheromone=0.0)

    @staticmethod
    def change_node_value(G, node, value):
        try:
            nx.set_node_attributes(G, {node: {'value': value}})
        except nx.NetworkXError:  # Knoten existiert nicht
            pass

    @staticmethod
    def delete_edge(G, tail, head):
        # Entfernen der Kante zum Graphen
        try:
            G.remove_edge(tail, head)

            # Lösche Knoten, falls keine Kante mehr dazu existiert
            if G.degree[tail] == 0:
                G.remove_node(tail)
            if G.degree[head] == 0:
                G.remove_node(head)
        except nx.NetworkXError:  # Kante existiert nicht
            pass