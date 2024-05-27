import json
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib import animation, gridspec
import matplotlib.colors as mcolors
import matplotlib as mpl
import networkx as nx
from matplotlib.widgets import Button, TextBox, CheckButtons
from colony import AntColonyRunner
from graph_tools import GraphTools


class AcoPlot:
    G: nx.DiGraph  # The Graph
    pos: dict  # positions for the nodes
    ants_config: dict  # config for the ants
    colony: AntColonyRunner  # the colony driver
    plot_config: dict  # config for the plot

    show_edge_parameters: bool = True  # if parameters (weights, pheromones) on the edge shall be shown, uses a lo of calculation time
    show_ant_animation: bool = True  # if the steps and paths of the ants shall be shown
    node_label_color: str = 'white'  # color of the label of the node
    node_label_size: int = 12  # font size of the node label
    edge_weight_label_color: str = 'red'  # color for the weight parameter shown for edges
    edge_pheromone_label_color: str = 'blue'  # color for the pheromone parameter shown for edges
    ant_animation_color: str = 'red'  # color of the ant paths shown on the graph

    def init_config(self, config_path: str):
        """
        initializes parameters for the plot

        :param config_path: file path for the config file, that has to be loaded
        """

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

    """
        defines the buttons on the plot
    """
    def setup_buttons(self):
        gs = gridspec.GridSpec(7, 7, bottom=0, top=0.25, hspace=0.5, wspace=0.5)

        self.check_edge = CheckButtons(plt.subplot(gs[0, 0]), ['Parameter'], [self.show_edge_parameters])
        self.check_edge.on_clicked(self.update_check_edge)

        self.check_ant = CheckButtons(plt.subplot(gs[1, 0]), ['Animation'], [self.show_ant_animation])
        self.check_ant.on_clicked(self.update_check_ant)

        self.check_random_spawn = CheckButtons(plt.subplot(gs[2, 0]), ['Random Spawn'],
                                               [self.colony.waves[0].ant_random_spawn])
        self.check_random_spawn.on_clicked(self.toggle_random_spawn)

        self.check_put_pheromones_always = CheckButtons(plt.subplot(gs[3, 0]), ['Always Pheromones'],
                                                        [self.colony.waves[0].put_pheromones_always])
        self.check_put_pheromones_always.on_clicked(self.toggle_put_pheromones_always)

        self.check_prioritize_pheromone_routes = CheckButtons(plt.subplot(gs[4, 0]), ['Prioritize Pheromones'],
                                                              [self.colony.waves[0].prioritize_pheromone_routes])

        self.check_stop_on_success = CheckButtons(plt.subplot(gs[5, 0]), ['Stop on Success'],
                                                  [self.colony.waves[0].stop_on_success])
        self.check_stop_on_success.on_clicked(self.toggle_stop_on_success)

                        #-------------------------Second Row----------------------------#

        plt.subplot(gs[2, 3]).annotate('Iteration Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_iteration_sleep = TextBox(plt.subplot(gs[2, 3]), '',
                                               initial=str(self.colony.waves[0].iteration_sleep))
        self.textbox_iteration_sleep.on_submit(self.update_iteration_sleep)

        plt.subplot(gs[2, 4]).annotate('Step Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_step_sleep = TextBox(plt.subplot(gs[2, 4]), '', initial=str(self.colony.waves[0].step_sleep))
        self.textbox_step_sleep.on_submit(self.update_step_sleep)

        plt.subplot(gs[2, 5]).annotate('Wave Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_wave_sleep = TextBox(plt.subplot(gs[2, 5]), '', initial=str(self.colony.waves[0].wave_sleep))
        self.textbox_wave_sleep.on_submit(self.update_wave_sleep)

                        # -------------------------Third Row----------------------------#

        plt.subplot(gs[1, 3]).annotate('Alpha', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_alpha = TextBox(plt.subplot(gs[1, 3]), '', initial=str(self.colony.waves[0].alpha))

        plt.subplot(gs[1, 4]).annotate('Beta', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_beta = TextBox(plt.subplot(gs[1, 4]), '', initial=str(self.colony.waves[0].beta))

        plt.subplot(gs[1, 5]).annotate('Random Chance', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_random_chance = TextBox(plt.subplot(gs[1, 5]), '', initial=str(self.colony.waves[0].random_chance))

        self.update_params_button = Button(plt.subplot(gs[3, 3]), label='Update Params')
        self.update_params_button.on_clicked(self.update_parameters)


                        # -------------------------Fourth Row----------------------------#

        self.add_edge_button = Button(plt.subplot(gs[3, 1]), label='Add')
        self.add_edge_button.on_clicked(
            lambda event: self.add_edge(self.textbox_tail.text, self.textbox_head.text, self.textbox_weight.text))

        plt.subplot(gs[0, 1]).annotate('Start', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_head = TextBox(plt.subplot(gs[0, 1]), '')

        plt.subplot(gs[1, 1]).annotate('End', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_tail = TextBox(plt.subplot(gs[1, 1]), '')

        plt.subplot(gs[2, 1]).annotate('Weight', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_weight = TextBox(plt.subplot(gs[2, 1]), '')

        self.delete_edge_button = Button(plt.subplot(gs[4, 1]), label='Remove')
        self.delete_edge_button.on_clicked(
            lambda event: self.delete_edge(self.textbox_tail.text, self.textbox_head.text))

                        # -------------------------Fith Row----------------------------#
        plt.subplot(gs[0, 3]).annotate('Evap. Rate', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_evaporation_rate = TextBox(plt.subplot(gs[0, 3]), '',
                                                initial=str(self.colony.waves[0].evaporation_rate))

        plt.subplot(gs[0, 4]).annotate('Max. Steps', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_max_steps = TextBox(plt.subplot(gs[0, 4]), '', initial=str(self.colony.waves[0].ant_max_steps))

        plt.subplot(gs[0, 5]).annotate('Max. Iteration', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_max_iterations = TextBox(plt.subplot(gs[0, 5]), '',
                                              initial=str(self.colony.waves[0].max_iterations))

        plt.subplot(gs[0, 6]).annotate('Conc. Ants', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_concurrent_ants = TextBox(plt.subplot(gs[0, 6]), '',
                                               initial=str(self.colony.waves[0].concurrent_ants))

                        # -------------------------Sixth Row----------------------------#

        self.save_config_button = Button(plt.subplot(gs[5, 6]), label='Save Config')
        self.save_config_button.on_clicked(self.save_config)

        self.load_config_button = Button(plt.subplot(gs[5, 5]), label='Load Config')
        self.load_config_button.on_clicked(self.on_load_config_clicked)

        # self.toggle_buttons_button = Button(plt.subplot(gs[4, 3]), label='Hide Buttons')
        # self.toggle_buttons_button.on_clicked(self.toggle_buttons)

        self.start_colony_button = Button(plt.subplot(gs[3, 4]), label='Run Colony')
        self.start_colony_button.on_clicked(lambda event: self.colony.start())

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

    def update_ant_class(self, event):
        self.colony.waves[0].ant_class = event

    def toggle_random_spawn(self, label):
        self.colony.waves[0].random_spawn = not self.colony.waves[0].random_spawn

    def toggle_put_pheromones_always(self, label):
        self.colony.waves[0].put_pheromones_always = not self.colony.waves[0].put_pheromones_always

    def toggle_stop_on_success(self, label):
        self.colony.waves[0].stop_on_success = not self.colony.waves[0].stop_on_success

    def toggle_prioritize_pheromone_routes(self, label):
        self.colony.waves[0].prioritize_pheromone_routes = not self.colony.waves[0].prioritize_pheromone_routes

    def update_speed(self, val):
        self.speed_factor = val
        for wave in self.colony.waves:
            wave.step_sleep = 0.5 / self.speed_factor
            wave.iteration_sleep = 0.5 / self.speed_factor
            wave.wave_sleep = 0.5 / self.speed_factor
        print(f'Updated speed factor: {self.speed_factor}')

    def update_step_sleep(self, text):
        try:
            val = float(text)
            for wave in self.colony.waves:
                wave.step_sleep = val
        except ValueError:
            print("Please enter a valid number for step sleep.")

    def update_iteration_sleep(self, text):
        try:
            val = float(text)
            for wave in self.colony.waves:
                wave.iteration_sleep = val
        except ValueError:
            print("Please enter a valid number for iteration sleep.")

    def update_wave_sleep(self, text):
        try:
            val = float(text)
            for wave in self.colony.waves:
                wave.wave_sleep = val
        except ValueError:
            print("Please enter a valid number for wave sleep.")

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

    def save_config(self, event):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])

        if file_path:
            with open(file_path, 'w') as f:
                json.dump(GraphTools.save_config_as_json(self), f, indent=4)
            print(f"Configuration saved to {file_path}")

    def on_load_config_clicked(self, event):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.reset(file_path)

    def update_check_edge(self, label):
        self.show_edge_parameters = not self.show_edge_parameters

    def update_check_ant(self, label):
        self.show_ant_animation = not self.show_ant_animation

    def update_plot(self, frame):
        """
        renders the graph
        """
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
        edges = nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=list(edges), width=widths,
                                       edge_color=edge_colors,
                                       connectionstyle="arc3,rad=0.07", ax=self.ax)

        node_labels = nx.draw_networkx_labels(self.G, self.pos, font_size=self.node_label_size, ax=self.ax,
                                              font_color=self.node_label_color,
                                              labels={n: n for n in self.G.nodes()})

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
                    path_coords = [(self.pos[ant.path[i]], self.pos[ant.path[i + 1]]) for i in
                                   range(len(ant.path) - 1)]
                    for coords in path_coords:
                        path_line = self.ax.plot([coords[0][0], coords[1][0]], [coords[0][1], coords[1][1]],
                                                 color=self.ant_animation_color,
                                                 linestyle='-', linewidth=2)
                        artists.extend(path_line)

        try:
            if not self.colony.waves[0].ant_random_spawn:
                current_node_artists = nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, node_size=700,
                                                              nodelist=[self.colony.waves[0].ant_spawn_node],
                                                              node_color=self.ant_animation_color)
                artists.append(current_node_artists)
        except:
            pass

        return artists

    def add_edge(self, tail: str, head: str, weight: float, tail_value: float = None, head_value: float = None):
        """
        Adds an edge to the graph

        :param tail: outgoing node
        :param head: incoming node
        :param weight: weight of the edge
        :param tail_value: a value for the tail node. node values define possible targets for the ants
        :param head_value: a value for the head node
        """
        self.pos = GraphTools.add_edge(self.G, tail, head, weight, tail_value, head_value, self.pos)

    def delete_edge(self, tail, head):
        """
        Deletes an edge from the graph

        :param tail: outgoing node
        :param head: incoming node
        """
        self.pos = GraphTools.delete_edge(self.G, tail, head, self.pos)
