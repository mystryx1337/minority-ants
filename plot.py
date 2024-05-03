import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.colors as mcolors
import matplotlib as mpl
import networkx as nx
from matplotlib.widgets import Button, TextBox
import random
import colony
import json


class AcoPlot:
    G: nx.DiGraph
    pos: dict
    ants_config: dict
    colony: colony.AntColonyRunner

    def init_config(self):
        self.load_config_from_json()
        self.colony = colony.AntColonyRunner(self)

    def __init__(self):
        self.init_config()
        mpl.rcParams['toolbar'] = 'None'

        # colormaps  https://matplotlib.org/stable/users/explain/colors/colormaps.html
        self.cmap_cool = mpl.colormaps['cool']
        self.cmap_winter = mpl.colormaps['winter']

        # Status of the animation
        self.status = {'ants_running': False}

        #area for buttons
        self.pos = nx.spring_layout(self.G)  # positions for all nodes
        self.current_node = list(self.G.nodes())[0] if self.G.nodes() else None
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

        #buttons and input-fields
        ax_tail = self.fig.add_axes([0.25, 0.05, 0.05, 0.075])
        textbox_tail = TextBox(ax_tail, 'Start ')

        ax_head = self.fig.add_axes([0.35, 0.05, 0.05, 0.075])
        textbox_head = TextBox(ax_head, 'Ende ')

        ax_weight = self.fig.add_axes([0.45, 0.05, 0.05, 0.075])
        textbox_weight = TextBox(ax_weight, 'Weight ')

        add_edge_ax = self.fig.add_axes([0.1, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        add_edge_button = Button(add_edge_ax, label='Add')
        add_edge_button.on_clicked(lambda event: self.add_edge(textbox_tail.text, textbox_head.text,
                                                               textbox_weight.text))  # Füge den Callback hinzu

        delete_edge_ax = self.fig.add_axes([0.55, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        delete_edge_button = Button(delete_edge_ax, label='Remove')
        delete_edge_button.on_clicked(
            lambda event: self.delete_edge(textbox_tail.text, textbox_head.text))  # Füge den Callback hinzu

        start_colony_ax = self.fig.add_axes([0.75, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        start_colony_button = Button(start_colony_ax, label='Run Colony')
        start_colony_button.on_clicked(
            lambda event: self.colony.start())  # Füge den Callback hinzu

        # set focus to plot area
        plt.sca(self.ax)

        self.node = ["A"]  # Start node
        self.node_trace = [self.pos[self.node[0]]]  # Initialize trace list with starting node position


        # Change Frame for less flickering
        ani = animation.FuncAnimation(self.fig, self.update_plot, frames=200,
                                      interval=50, blit=True, repeat=True, fargs=())

        # keep the graph-window
        # self.ax = plt.gca()
        self.ax.margins(0.08)
        plt.axis("off")
        plt.show()

    def add_edges_from_outgoing_node(self, outgoing_node, target_nodes, edge_weights=None, edge_pheromones=None,
                                     node_value=0):
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

            self.G.add_edge(outgoing_node, target_node, weight=weight, pheromone=pheromone)

        nx.set_node_attributes(self.G, {outgoing_node: {'value': node_value}})

    def load_config_from_json(self):
        self.G = nx.DiGraph()

        # Opening JSON file
        f = open('configurations/test.json')

        data: dict = json.load(f)

        f.close()

        if 'macro' in data['nodes']:
            if data['nodes']['macro'] == 'fully_linked_graph':
                pass
            if data['nodes']['macro'] == '2d_grid_torus':
                pass
            if data['nodes']['macro'] == 'small_world':
                pass
        else:
            for node in data['nodes']:
                target_nodes: list[str] = data['nodes'][node]['edges']
                edge_weights: list[int] = data['nodes'][node]['weights'] if 'weights' in data['nodes'][node] else None
                pheromones: list[float] = data['nodes'][node]['pheromones'] if 'pheromones' in data['nodes'][node] else None
                node_value: int = data['nodes'][node]['value'] if 'value' in data['nodes'][node] else 0
                self.add_edges_from_outgoing_node(node, target_nodes, edge_weights=edge_weights, edge_pheromones=pheromones,
                                             node_value=node_value)

        self.ants_config = data['ants']


    def update_plot(self, frame):
        # Compute minimum and maximum values for normalization
        min_weight, max_weight = min(data['weight'] for _, _, data in self.G.edges(data=True)), max(
            data['weight'] for _, _, data in self.G.edges(data=True))
        min_pheromone, max_pheromone = min(data['pheromone'] for _, _, data in self.G.edges(data=True)), max(
            data['pheromone'] for _, _, data in self.G.edges(data=True))
        min_value, max_value = min(data['value'] for _, data in self.G.nodes(data=True)), max(
            data['value'] for _, data in self.G.nodes(data=True))

        # Define normalization and color mapping
        node_norm = mcolors.Normalize(vmin=min_value, vmax=max_value)
        edge_norm = mcolors.Normalize(vmin=min_pheromone, vmax=max_pheromone)
        
        self.ax.clear()

        # Draw nodes with updated properties
        node_colors = [self.cmap_winter(node_norm(data['value'])) for _, data in self.G.nodes(data=True)]
        nodes = nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=list(self.G.nodes()), node_color=node_colors,
                                       ax=self.ax)

        # Draw edges with updated properties
        edges = self.G.edges(data=True)
        edge_colors = [self.cmap_cool(edge_norm(data['pheromone'])) for _, _, data in edges]
        widths = [1 + (data['weight'] - min_weight) / (max_weight - min_weight) for _, _, data in edges]
        edges = nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=list(edges), width=widths, edge_color=edge_colors,
                                       connectionstyle="arc3,rad=0.07", ax=self.ax)

        # Node labels
        node_labels = nx.draw_networkx_labels(self.G, self.pos, font_size=12, font_color="white",
                                              labels={n: n for n in self.G.nodes()}, ax=self.ax)

        # Edge labels for weight
        weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
        edge_weight_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels, font_color='red',
                                                          label_pos=0.1, ax=self.ax)

        # Edge labels for pheromone
        pheromone_labels = {(tail, head): f"{round(data['pheromone'],1)}" for tail, head, data in self.G.edges(data=True)}
        edge_pheromone_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels,
                                                             font_color='blue', label_pos=0.3, ax=self.ax)

        # Collect all artists that need to be returned for blitting to work correctly
        artists = [nodes] + list(edges) + list(node_labels.values()) + list(edge_weight_labels.values()) + list(
            edge_pheromone_labels.values())

        if len(self.colony.ants) > 0:
            # Draw all ants as red dots
            ant_positions = [ant.current_node for ant in self.colony.ants]
            current_node_artists = nx.draw_networkx_nodes(self.G, self.pos, nodelist=ant_positions, node_color='red',
                                                          node_size=700, ax=self.ax)
            artists.append(current_node_artists)

            # Draw paths for each ant
            for ant in self.colony.ants:
                if len(ant.path) > 1:  # Check if there are at least two nodes in the path to form a line
                    # Extract positions for each node in the path
                    path_coords = [(self.pos[ant.path[i]], self.pos[ant.path[i + 1]]) for i in range(len(ant.path) - 1)]
                    # Draw lines between each pair of successive nodes
                    for coords in path_coords:
                        path_line = self.ax.plot([coords[0][0], coords[1][0]], [coords[0][1], coords[1][1]],
                                                 color='red',
                                                 linestyle='-', linewidth=2)
                        artists.extend(path_line)

        return artists

    def add_edge(self, tail, head, weight, tail_value=None, head_value=None):
        global G, pos

        try:
            weight = float(weight)
        except ValueError:
            weight = 1.0  # Set default weight if conversion fails

        # Change node value
        if tail == '' and head != '':
            self.change_node_value(head, weight)
            return
        if tail != '' and head == '':
            self.change_node_value(tail, weight)
            return

        # Add or update nodes with the specified or default 'value'
        if not self.G.has_node(tail):
            self.G.add_node(tail, value=tail_value if tail_value is not None else 0)  # Set a default or specified value
        else:
            if tail_value is not None:
                self.G.nodes[tail]['value'] = tail_value  # Update the value if specified

        if not self.G.has_node(head):
            self.G.add_node(head, value=head_value if head_value is not None else 0)  # Set a default or specified value
        else:
            if head_value is not None:
                self.G.nodes[head]['value'] = head_value  # Update the value if specified

        # Add the edge with weight and pheromone
        self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
        self.pos = nx.spring_layout(self.G)

    def change_node_value(self, node, value):
        try:
            nx.set_node_attributes(self.G, {node: {'value': value}})
        except nx.NetworkXError:  # Knoten existiert nicht
            pass

    def delete_edge(self, tail, head):
        # Entfernen der Kante zum Graphen
        try:
            self.G.remove_edge(tail, head)

            # Lösche Knoten, falls keine Kante mehr dazu existiert
            if self.G.degree[tail] == 0:
                self.G.remove_node(tail)
                self.pos = nx.spring_layout(self.G)  # Recalculate layout
            if self.G.degree[head] == 0:
                self.G.remove_node(head)
                self.pos = nx.spring_layout(self.G)  # Recalculate layout
        except nx.NetworkXError:  # Kante existiert nicht
            pass
