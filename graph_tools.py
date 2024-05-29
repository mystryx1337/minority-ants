import json
import string
import networkx as nx
import numpy as np


class GraphTools:
    """
    A collection of graph tools
    """

    @staticmethod
    def load_config_from_json(path):
        G = nx.DiGraph()

        # Opening JSON file
        with open(path, 'r') as f:
            data = json.load(f)

        # Macro configuration
        if 'macro' in data['nodes']:
            macro_config = data['nodes']['macro']
            if macro_config['type'] == 'fully_linked_graph':
                nodes = GraphTools.generate_nodes(macro_config['x'])
                for node in nodes:
                    exclusive_nodes = nodes.copy()
                    exclusive_nodes.remove(node)
                    GraphTools.add_edges_from_outgoing_node(G, node, exclusive_nodes)
            elif macro_config['type'] == '2d_grid_torus':
                x = macro_config['x']
                y = macro_config['y']
                pos = {}
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
                        pos[node] = np.array([i * 100, j * 100])
            elif macro_config['type'] == 'small_world':
                # Add your small world graph logic here
                pass

        # Other nodes configuration
        for node, node_config in data['nodes'].items():
            if node != 'macro':
                target_nodes = node_config.get('edges', [])
                edge_weights = node_config.get('weights', None)
                pheromones = node_config.get('pheromones', None)
                node_value = node_config.get('value', 0)
                GraphTools.add_edges_from_outgoing_node(G, node, target_nodes, edge_weights=edge_weights,
                                                        edge_pheromones=pheromones, node_value=node_value)

        if 'pos' not in locals():
            pos = nx.spring_layout(G)  # positions for all nodes if not 2d_grid_torus

        # Ensure default values for ants and plot configurations
        ants_config = data.get('ants', {})
        plot_config = data.get('plot', {})

        return G, ants_config, plot_config, pos

    @staticmethod
    def generate_nodes(n: int) -> list[str]:
        """
        Generates node names

        :return: a list[str] of node names
        """
        alphabet = list(string.ascii_uppercase)
        if n <= 26:
            return alphabet[0:n]
        else:
            double_alphabet = [letter1 + letter2 for letter1 in alphabet for letter2 in alphabet]
            return double_alphabet[0:n]

    @staticmethod
    def save_config_as_json(self):
        wave_config = self.colony.waves[0].to_dict()

        config_data = {
            'nodes': {
                'macro': {
                    'type': self.plot_config.get('macro_type', '2d_grid_torus'),
                    'x': self.plot_config.get('macro_x', 9),
                    'y': self.plot_config.get('macro_y', 9)
                }
            },
            'ants': [
                wave_config
            ],
            'plot': {
                'show_edge_parameters': self.show_edge_parameters,
                'show_ant_animation': self.show_ant_animation,
                'node_label_color': self.node_label_color,
                'node_label_size': self.node_label_size,
                'edge_weight_label_color': self.edge_weight_label_color,
                'edge_pheromone_label_color': self.edge_pheromone_label_color,
                'ant_animation_color': self.ant_animation_color,
                'cmap_edges': self.plot_config.get('cmap_edges', 'cool'),
                'cmap_nodes': self.plot_config.get('cmap_nodes', 'winter')
            }
        }

        for node, data in self.G.nodes(data=True):
            config_data['nodes'][node] = {
                'value': data.get('value', 0),
                'edges': list(self.G.successors(node)),
                'weights': [self.G[node][succ]['weight'] for succ in self.G.successors(node)],
                'pheromones': [self.G[node][succ]['pheromone'] for succ in self.G.successors(node)]
            }

        return config_data

    @staticmethod
    def add_edges_from_outgoing_node(G: nx.DiGraph, outgoing_node: str, target_nodes: list[str], edge_weights=None,
                                     edge_pheromones=None, node_value=0):
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
                if not G.has_node(target_node):
                    nx.set_node_attributes(G, {target_node: {'value': 0}})

                weight = 1
                if edge_weights is not None:
                    weight = edge_weights[i]

                pheromone = 0.0
                if edge_pheromones is not None:
                    pheromone = edge_pheromones[i]

                G.add_edge(outgoing_node, target_node, weight=weight, pheromone=pheromone)

        nx.set_node_attributes(G, {outgoing_node: {'value': node_value}})

    @staticmethod
    def add_edge(G: nx.DiGraph, tail: str, head: str, weight: float, tail_value: float = None, head_value: float = None,
                 pos: dict = None) -> dict:
        """
        Adds an edge to the graph

        :param G: the Graph
        :param tail: outgoing node
        :param head: incoming node
        :param weight: weight of the edge
        :param tail_value: value parameter for the tail node
        :param head_value: value parameter for the head node
        :param pos: current positions of the nodes
        :return: new positions for the nodes
        """
        if pos is None:
            pos = []

        try:
            weight = float(weight)
        except ValueError:
            weight = 1.0  # Set default weight if conversion fails

        # Change node value
        if tail == '' and head != '':
            GraphTools.change_node_value(G, head, weight)
            return pos
        if tail != '' and head == '':
            GraphTools.change_node_value(G, tail, weight)
            return pos

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
        return nx.spring_layout(G)

    @staticmethod
    def change_node_value(G: nx.DiGraph, node: str, value):
        try:
            nx.set_node_attributes(G, {node: {'value': value}})
        except nx.NetworkXError:  # Knoten existiert nicht
            pass

    @staticmethod
    def delete_edge(G: nx.DiGraph, tail: str, head: str, pos: dict) -> dict:
        # Entfernen der Kante zum Graphen
        try:
            G.remove_edge(tail, head)

            # Lösche Knoten, falls keine Kante mehr dazu existiert
            if G.degree[tail] == 0:
                G.remove_node(tail)
                pos.pop(tail)
            if G.degree[head] == 0:
                G.remove_node(head)
                pos.pop(head)
        except nx.NetworkXError:  # Kante existiert nicht
            pass

        return pos
