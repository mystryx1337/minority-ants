import json
import string
import networkx as nx
import numpy as np


class GraphTools:
    @staticmethod
    def load_config_from_json(path):
        G = nx.DiGraph()

        # Opening JSON file
        f = open(path)

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
                pos: dict = {}
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

        if data['nodes']['macro']['type'] != '2d_grid_torus':
            pos = nx.spring_layout(G)  # positions for all nodes

        if not 'ants' in data:
            data['ants'] = {}

        if not 'plot' in data:
            data['plot'] = {}

        return G, data['ants'], data['plot'], pos

    @staticmethod
    def generate_nodes(n: int):
        alphabet = list(string.ascii_uppercase)
        if n <= 26:
            return alphabet[0:n]
        else:
            double_alphabet = [letter1 + letter2 for letter1 in alphabet for letter2 in alphabet]
            return double_alphabet[0:n]

    @staticmethod
    def save_config_as_json(self):
        config_data = {
            'nodes': {
                'macro': {
                    'type': self.plot_config.get('macro_type', '2d_grid_torus'),
                    'x': self.plot_config.get('macro_x', 9),
                    'y': self.plot_config.get('macro_y', 9)
                }
            },
            'ants': [
                {
                    'alpha': self.colony.waves[0].alpha,
                    'beta': self.colony.waves[0].beta,
                    'random_chance': self.colony.waves[0].random_chance,
                    'step_sleep': self.colony.waves[0].step_sleep,
                    'iteration_sleep': self.colony.waves[0].iteration_sleep,
                    'wave_sleep': self.colony.waves[0].wave_sleep,
                }],
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
                                     edge_pheromones=None,
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
    def add_edge(G, tail, head, weight, tail_value=None, head_value=None, pos=None) -> dict:
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
    def change_node_value(G, node, value):
        try:
            nx.set_node_attributes(G, {node: {'value': value}})
        except nx.NetworkXError:  # Knoten existiert nicht
            pass

    @staticmethod
    def delete_edge(G, tail, head, pos: dict) -> dict:
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
