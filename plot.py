import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.colors as mcolors
import matplotlib as mpl
import networkx as nx
from matplotlib.widgets import Button, TextBox
from colony import AntColonyRunner
from graph_tools import GraphTools


class AcoPlot:
    G: nx.DiGraph
    pos: dict
    ants_config: dict
    colony: AntColonyRunner
    plot_config: dict

    show_edge_parameters: bool = True
    show_ant_animation: bool = True
    node_label_color: str = 'white'
    node_label_size: int = 12
    edge_weight_label_color: str = 'red'
    edge_pheromone_label_color: str = 'blue'
    ant_animation_color: str = 'red'

    def init_config(self):
        self.G, self.ants_config, self.plot_config, self.pos = GraphTools.load_config_from_json()
        self.colony = AntColonyRunner(self)

        self.show_edge_parameters = self.plot_config['show_edge_parameters'] if 'show_edge_parameters' in self.plot_config else True
        self.show_ant_animation = self.plot_config['show_ant_animation'] if 'show_ant_animation' in self.plot_config else True
        self.node_label_color = self.plot_config['node_label_color'] if 'node_label_color' in self.plot_config else 'white'
        self.node_label_size = self.plot_config['node_label_size'] if 'node_label_size' in self.plot_config else 12
        self.edge_weight_label_color = self.plot_config['edge_weight_label_color'] if 'edge_weight_label_color' in self.plot_config else 'red'
        self.edge_pheromone_label_color = self.plot_config['edge_pheromone_label_color'] if 'edge_pheromone_label_color' in self.plot_config else 'blue'
        self.ant_animation_color = self.plot_config['ant_animation_color'] if 'ant_animation_color' in self.plot_config else 'red'

        # colormaps  https://matplotlib.org/stable/users/explain/colors/colormaps.html
        mpl.rcParams['toolbar'] = 'None'
        self.cmap_edges = mpl.colormaps[self.plot_config['cmap_edges']] if 'cmap_edges' in self.plot_config else mpl.colormaps['cool']
        self.cmap_nodes = mpl.colormaps[self.plot_config['cmap_nodes']] if 'cmap_nodes' in self.plot_config else mpl.colormaps['winter']

    def __init__(self):
        self.init_config()

        # Status of the animation
        self.status = {'ants_running': False}

        #area for buttons
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

        # Change Frame for less flickering
        ani = animation.FuncAnimation(self.fig, self.update_plot, frames=200,
                                      interval=50, blit=True, repeat=True, fargs=())

        # keep the graph-window
        # self.ax = plt.gca()
        self.ax.margins(0.08)
        plt.axis("off")
        plt.show()

        self.colony.stop()

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
        node_colors = [self.cmap_nodes(node_norm(data['value'])) for _, data in self.G.nodes(data=True)]
        nodes = nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=list(self.G.nodes()), node_color=node_colors,
                                       ax=self.ax)

        # Draw edges with updated properties
        edges = self.G.edges(data=True)
        edge_colors = [self.cmap_edges(edge_norm(data['pheromone'])) for _, _, data in edges]
        widths = [1 + (data['weight'] - min_weight) / (max_weight - min_weight + 1) for _, _, data in edges]
        edges = nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=list(edges), width=widths, edge_color=edge_colors,
                                       connectionstyle="arc3,rad=0.07", ax=self.ax)

        # Node labels
        node_labels = nx.draw_networkx_labels(self.G, self.pos, font_size=self.node_label_size, ax=self.ax,
                                              font_color=self.node_label_color, labels={n: n for n in self.G.nodes()})

        if self.show_edge_parameters:
            # Edge labels for weight
            weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
            edge_weight_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels,
                                                              font_color=self.edge_weight_label_color,
                                                              label_pos=0.1, ax=self.ax)

            # Edge labels for pheromone
            pheromone_labels = {(tail, head): f"{round(data['pheromone'], 1)}" for tail, head, data in
                                self.G.edges(data=True)}
            edge_pheromone_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels,
                                                                 font_color=self.edge_pheromone_label_color,
                                                                 label_pos=0.3, ax=self.ax)

            # Collect all artists that need to be returned for blitting to work correctly
            artists = [nodes] + list(edges) + list(node_labels.values()) + list(edge_weight_labels.values()) + list(
                edge_pheromone_labels.values())
        else:
            artists = [nodes] + list(edges) + list(node_labels.values())

        if len(self.colony.ants) > 0 and self.show_ant_animation:
            # Draw all ants as red dots
            ant_positions = [ant.current_node for ant in self.colony.ants]
            current_node_artists = nx.draw_networkx_nodes(self.G, self.pos, nodelist=ant_positions, node_size=700,
                                                          node_color=self.ant_animation_color, ax=self.ax)
            artists.append(current_node_artists)

            # Draw paths for each ant
            for ant in self.colony.ants:
                if len(ant.path) > 1:  # Check if there are at least two nodes in the path to form a line
                    # Extract positions for each node in the path
                    path_coords = [(self.pos[ant.path[i]], self.pos[ant.path[i + 1]]) for i in range(len(ant.path) - 1)]
                    # Draw lines between each pair of successive nodes
                    for coords in path_coords:
                        path_line = self.ax.plot([coords[0][0], coords[1][0]], [coords[0][1], coords[1][1]],
                                                 color=self.ant_animation_color,
                                                 linestyle='-', linewidth=2)
                        artists.extend(path_line)

        return artists

    def add_edge(self, tail, head, weight, tail_value=None, head_value=None):
        self.pos = GraphTools.add_edge(self.G, tail, head, weight, tail_value, head_value, self.pos)

    def delete_edge(self, tail, head):
        self.pos = GraphTools.delete_edge(self.G, tail, head, self.pos)  # Recalculate layout
