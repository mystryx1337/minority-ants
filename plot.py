import tkinter as tk
from tkinter import filedialog
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

    def init_config(self, config_path):
        self.G, self.ants_config, self.plot_config, self.pos = GraphTools.load_config_from_json(config_path)
        self.colony = AntColonyRunner(self)

        self.show_edge_parameters = self.plot_config.get('show_edge_parameters', True)
        self.show_ant_animation = self.plot_config.get('show_ant_animation', True)
        self.node_label_color = self.plot_config.get('node_label_color', 'white')
        self.node_label_size = self.plot_config.get('node_label_size', 12)
        self.edge_weight_label_color = self.plot_config.get('edge_weight_label_color', 'red')
        self.edge_pheromone_label_color = self.plot_config.get('edge_pheromone_label_color', 'blue')
        self.ant_animation_color = self.plot_config.get('ant_animation_color', 'red')

        mpl.rcParams['toolbar'] = 'None'
        self.cmap_edges = mpl.colormaps.get(self.plot_config.get('cmap_edges', 'cool'))
        self.cmap_nodes = mpl.colormaps.get(self.plot_config.get('cmap_nodes', 'winter'))

    def __init__(self, config_path):
        self.init_config(config_path)
        self.status = {'ants_running': False}
        self.buttons_visible = True
        self.setup_plot()

    def setup_plot(self):
        self.current_node = list(self.G.nodes())[0] if self.G.nodes() else None
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.3)
        self.setup_buttons()
        plt.sca(self.ax)
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, frames=200,
                                           interval=50, blit=True, repeat=True, fargs=())
        self.ax.margins(0.08)
        plt.axis("off")
        plt.show()
        self.colony.stop()

    def setup_buttons(self):
        ax_tail = self.fig.add_axes([0.25, 0.05, 0.05, 0.05])
        self.textbox_tail = TextBox(ax_tail, 'Start ')

        ax_head = self.fig.add_axes([0.35, 0.05, 0.05, 0.05])
        self.textbox_head = TextBox(ax_head, 'Ende ')

        ax_weight = self.fig.add_axes([0.45, 0.05, 0.05, 0.05])
        self.textbox_weight = TextBox(ax_weight, 'Weight ')

        add_edge_ax = self.fig.add_axes([0.1, 0.05, 0.1, 0.05])
        self.add_edge_button = Button(add_edge_ax, label='Add')
        self.add_edge_button.on_clicked(lambda event: self.add_edge(self.textbox_tail.text, self.textbox_head.text,
                                                                    self.textbox_weight.text))

        delete_edge_ax = self.fig.add_axes([0.55, 0.05, 0.1, 0.05])
        self.delete_edge_button = Button(delete_edge_ax, label='Remove')
        self.delete_edge_button.on_clicked(
            lambda event: self.delete_edge(self.textbox_tail.text, self.textbox_head.text))

        start_colony_ax = self.fig.add_axes([0.7, 0.05, 0.1, 0.05])
        self.start_colony_button = Button(start_colony_ax, label='Run Colony')
        self.start_colony_button.on_clicked(lambda event: self.colony.start())

        load_config_ax = self.fig.add_axes([0.82, 0.05, 0.1, 0.05])
        self.load_config_button = Button(load_config_ax, label='Load Config')
        self.load_config_button.on_clicked(self.on_load_config_clicked)


        ax_alpha = self.fig.add_axes([0.25, 0.15, 0.05, 0.05])
        self.textbox_alpha = TextBox(ax_alpha, 'Alpha', initial=str(self.colony.waves[0].alpha))

        ax_beta = self.fig.add_axes([0.35, 0.15, 0.05, 0.05])
        self.textbox_beta = TextBox(ax_beta, 'Beta', initial=str(self.colony.waves[0].beta))

        ax_random_chance = self.fig.add_axes([0.45, 0.15, 0.05, 0.05])
        self.textbox_random_chance = TextBox(ax_random_chance, 'Rand',
                                             initial=str(self.colony.waves[0].random_chance))


        update_params_ax = self.fig.add_axes([0.55, 0.15, 0.1, 0.05])
        self.update_params_button = Button(update_params_ax, label='Update Params')
        self.update_params_button.on_clicked(self.update_parameters)

        # Add toggle button for hiding/showing GUI elements
        toggle_buttons_ax = self.fig.add_axes([0.7, 0.15, 0.1, 0.05])
        self.toggle_buttons_button = Button(toggle_buttons_ax, label='Hide Buttons')
        self.toggle_buttons_button.on_clicked(self.toggle_buttons)

    def update_parameters(self, event):
        try:
            alpha = float(self.textbox_alpha.text)
            beta = float(self.textbox_beta.text)
            random_chance = float(self.textbox_random_chance.text)

            for wave in self.colony.waves:
                wave.alpha = alpha
                wave.beta = beta
                wave.random_chance = random_chance

            print(f'Updated parameters: Alpha={alpha}, Beta={beta}, Random Chance={random_chance}')
        except ValueError:
            print("Please enter valid numerical values for alpha, beta, and random chance.")

    def toggle_buttons(self, event):
        self.buttons_visible = not self.buttons_visible

        # Toggle visibility of TextBox widgets
        self.textbox_tail.ax.set_visible(self.buttons_visible)
        self.textbox_head.ax.set_visible(self.buttons_visible)
        self.textbox_weight.ax.set_visible(self.buttons_visible)
        self.textbox_alpha.ax.set_visible(self.buttons_visible)
        self.textbox_beta.ax.set_visible(self.buttons_visible)
        self.textbox_random_chance.ax.set_visible(self.buttons_visible)

        # Toggle visibility of Button widgets
        self.add_edge_button.ax.set_visible(self.buttons_visible)
        self.delete_edge_button.ax.set_visible(self.buttons_visible)
        # self.start_colony_button.ax.set_visible(self.buttons_visible)
        # self.load_config_button.ax.set_visible(self.buttons_visible)
        self.update_params_button.ax.set_visible(self.buttons_visible)

        # Update the label of the toggle button
        if self.buttons_visible:
            self.toggle_buttons_button.label.set_text('Hide Buttons')
        else:
            self.toggle_buttons_button.label.set_text('Show Buttons')

        plt.draw()

    def reset(self, config_path):
        self.colony.stop()
        plt.close(self.fig)
        self.init_config(config_path)
        self.setup_plot()

    def on_load_config_clicked(self, event):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.reset(file_path)

    def update_plot(self, frame):
        min_weight, max_weight = min(data['weight'] for _, _, data in self.G.edges(data=True)), max(
            data['weight'] for _, _, data in self.G.edges(data=True))
        min_pheromone, max_pheromone = min(data['pheromone'] for _, _, data in self.G.edges(data=True)), max(
            data['pheromone'] for _, _, data in self.G.edges(data=True))
        min_value, max_value = min(data['value'] for _, data in self.G.nodes(data=True)), max(
            data['value'] for _, data in self.G.nodes(data=True))

        node_norm = mcolors.Normalize(vmin=min_value, vmax=max_value)
        edge_norm = mcolors.Normalize(vmin=min_pheromone, vmax=max_pheromone)

        self.ax.clear()

        node_colors = [self.cmap_nodes(node_norm(data['value'])) for _, data in self.G.nodes(data=True)]
        nodes = nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=list(self.G.nodes()), node_color=node_colors,
                                       ax=self.ax)

        edges = self.G.edges(data=True)
        edge_colors = [self.cmap_edges(edge_norm(data['pheromone'])) for _, _, data in edges]
        widths = [1 + (data['weight'] - min_weight) / (max_weight - min_weight + 1) for _, _, data in edges]
        edges = nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=list(edges), width=widths, edge_color=edge_colors,
                                       connectionstyle="arc3,rad=0.07", ax=self.ax)

        node_labels = nx.draw_networkx_labels(self.G, self.pos, font_size=self.node_label_size, ax=self.ax,
                                              font_color=self.node_label_color, labels={n: n for n in self.G.nodes()})

        if self.show_edge_parameters:
            weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
            edge_weight_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels,
                                                              font_color=self.edge_weight_label_color,
                                                              label_pos=0.1, ax=self.ax)

            pheromone_labels = {(tail, head): f"{round(data['pheromone'], 1)}" for tail, head, data in
                                self.G.edges(data=True)}
            edge_pheromone_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels,
                                                                 font_color=self.edge_pheromone_label_color,
                                                                 label_pos=0.3, ax=self.ax)

            artists = [nodes] + list(edges) + list(node_labels.values()) + list(edge_weight_labels.values()) + list(
                edge_pheromone_labels.values())
        else:
            artists = [nodes] + list(edges) + list(node_labels.values())

        if len(self.colony.ants) > 0 and self.show_ant_animation:
            ant_positions = [ant.current_node for ant in self.colony.ants]
            current_node_artists = nx.draw_networkx_nodes(self.G, self.pos, nodelist=ant_positions, node_size=700,
                                                          node_color=self.ant_animation_color, ax=self.ax)
            artists.append(current_node_artists)

            for ant in self.colony.ants:
                if len(ant.path) > 1:
                    path_coords = [(self.pos[ant.path[i]], self.pos[ant.path[i + 1]]) for i in range(len(ant.path) - 1)]
                    for coords in path_coords:
                        path_line = self.ax.plot([coords[0][0], coords[1][0]], [coords[0][1], coords[1][1]],
                                                 color=self.ant_animation_color,
                                                 linestyle='-', linewidth=2)
                        artists.extend(path_line)

        return artists

    def add_edge(self, tail, head, weight, tail_value=None, head_value=None):
        self.pos = GraphTools.add_edge(self.G, tail, head, weight, tail_value, head_value, self.pos)

    def delete_edge(self, tail, head):
        self.pos = GraphTools.delete_edge(self.G, tail, head, self.pos)
