import json
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib import animation, gridspec
import matplotlib.colors as mcolors
import matplotlib as mpl
import networkx as nx
from matplotlib.widgets import Button, TextBox, CheckButtons, RadioButtons
from aco_routing.ant_colony_runner import AntColonyRunner
from graph_tools import GraphTools


class Plot:
    G: nx.DiGraph  # The Graph
    pos: dict  # positions for the nodes
    ants_config: dict  # config for the ants
    colony: AntColonyRunner  # the colony driver
    plot_config: dict  # config for the plot

    show_edge_parameters: bool = True  # if parameters (weights, pheromones) on the edge shall be shown, uses a lot of calculation time
    show_ant_animation: bool = True  # if the steps and paths of the ants shall be shown
    show_graph: bool = True  # if the graph shall be shown
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
        self.colony = AntColonyRunner(self, self.print_message)

        self.show_edge_parameters = self.plot_config.get('show_edge_parameters', True)
        self.show_ant_animation = self.plot_config.get('show_ant_animation', True)
        self.show_graph = self.plot_config.get('show_graph', True)
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
        """
        Set up the plot for visualizing the graph and ants' movement.

        Steps performed:
        1. Set the current node to the first node in the graph (if available).
        2. Create a figure and axes for the plot.
        3. Adjust the layout to make space for buttons.
        4. Set up the control buttons.
        5. Initialize the animation for updating the plot.
        6. Adjust the margins and turn off the axis.
        7. Display the plot.
        8. Stop the colony's activity.

        :return: None
        """

        self.current_node = list(self.G.nodes())[0] if self.G.nodes() else None
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.3)
        self.setup_buttons()
        plt.sca(self.ax)
        if self.show_graph:
            self.ani = animation.FuncAnimation(self.fig, self.update_plot, frames=200,
                                               interval=50, blit=True, repeat=True, fargs=())
        self.ax.margins(0.08)
        plt.axis("off")

        plt.show()
        self.colony.stop()

    def setup_buttons(self):
        """
        defines the buttons and input fields on the plot uses an 8 x 7 gridlayout
        """
        gs = gridspec.GridSpec(8, 7, bottom=0, top=0.25, hspace=0.5, wspace=0.5)

        self.check_edge = CheckButtons(plt.subplot(gs[0, 0]), ['Parameter'], [self.show_edge_parameters])
        self.check_edge.on_clicked(self.update_check_edge)

        self.check_ant = CheckButtons(plt.subplot(gs[1, 0]), ['Animation'], [self.show_ant_animation])
        self.check_ant.on_clicked(self.update_check_ant)

        self.check_put_pheromones_always = CheckButtons(plt.subplot(gs[2, 0]), ['Always Pheromones'],
                                                        [self.colony.waves[0].put_pheromones_always])
        self.check_put_pheromones_always.on_clicked(self.toggle_put_pheromones_always)

        self.check_prioritize_pheromone_routes = CheckButtons(plt.subplot(gs[3, 0]), ['Prioritize Pheromones'],
                                                              [self.colony.waves[0].prioritize_pheromone_routes])
        self.check_prioritize_pheromone_routes.on_clicked(self.toggle_prioritize_pheromone_routes)

        self.check_stop_on_success = CheckButtons(plt.subplot(gs[4, 0]), ['Stop on Success'],
                                                  [self.colony.waves[0].stop_on_success])
        self.check_stop_on_success.on_clicked(self.toggle_stop_on_success)

        self.check_show_graph = CheckButtons(plt.subplot(gs[5, 0]), ['Show Graph'],
                                                  [self.graph_visibly])
        self.check_show_graph.on_clicked(self.graph_visibly)

        #-------------------------Second Row----------------------------#

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

        # -------------------------Third Row----------------------------#
        self.check_random_spawn = CheckButtons(plt.subplot(gs[0, 2]), ['Random Spawn'],
                                               [self.colony.waves[0].ant_random_spawn])
        self.check_random_spawn.on_clicked(self.toggle_random_spawn)

        plt.subplot(gs[1, 2]).annotate('Spawn Node', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_spawn_node = TextBox(plt.subplot(gs[1, 2]), '', initial=str(self.colony.waves[0].ant_spawn_node))
        self.textbox_spawn_node.on_submit(self.update_spawn_node)
        if self.colony.waves[0].ant_random_spawn:
            self.textbox_spawn_node.set_active(False)

        # -------------------------Fourth Row----------------------------#
        plt.subplot(gs[0, 3]).annotate('Iteration Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_iteration_sleep = TextBox(plt.subplot(gs[0, 3]), '',
                                               initial=str(self.colony.waves[0].iteration_sleep))
        self.textbox_iteration_sleep.on_submit(self.update_iteration_sleep)

        plt.subplot(gs[1, 3]).annotate('Step Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_step_sleep = TextBox(plt.subplot(gs[1, 3]), '', initial=str(self.colony.waves[0].step_sleep))
        self.textbox_step_sleep.on_submit(self.update_step_sleep)

        plt.subplot(gs[2, 3]).annotate('Wave Sleep', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_wave_sleep = TextBox(plt.subplot(gs[2, 3]), '', initial=str(self.colony.waves[0].wave_sleep))
        self.textbox_wave_sleep.on_submit(self.update_wave_sleep)

        self.load_config_button = Button(plt.subplot(gs[3, 3]), label='Load Config')
        self.load_config_button.on_clicked(self.on_load_config_clicked)

        # -------------------------Fourth Row----------------------------#

        plt.subplot(gs[0, 4]).annotate('Alpha', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_alpha = TextBox(plt.subplot(gs[0, 4]), '', initial=str(self.colony.waves[0].alpha))

        plt.subplot(gs[1, 4]).annotate('Beta', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_beta = TextBox(plt.subplot(gs[1, 4]), '', initial=str(self.colony.waves[0].beta))

        plt.subplot(gs[2, 4]).annotate('Random Chance', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_random_chance = TextBox(plt.subplot(gs[2, 4]), '', initial=str(self.colony.waves[0].random_chance))

        self.save_config_button = Button(plt.subplot(gs[3, 4]), label='Save Config')
        self.save_config_button.on_clicked(self.save_config)

        # -------------------------Sixth Row----------------------------#
        plt.subplot(gs[0, 5]).annotate('Evap. Rate', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_evaporation_rate = TextBox(plt.subplot(gs[0, 5]), '',
                                                initial=str(self.colony.waves[0].evaporation_rate))

        plt.subplot(gs[1, 5]).annotate('Max. Steps', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_ant_max_steps = TextBox(plt.subplot(gs[1, 5]), '', initial=str(self.colony.waves[0].ant_max_steps))

        plt.subplot(gs[2, 5]).annotate('Max. Iteration', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_max_iterations = TextBox(plt.subplot(gs[2, 5]), '',
                                              initial=str(self.colony.waves[0].max_iterations))

        self.update_params_button = Button(plt.subplot(gs[3, 5]), label='Update Params')
        self.update_params_button.on_clicked(self.update_parameters)


        # -------------------------Seventh Row----------------------------#
        plt.subplot(gs[2, 6]).annotate('Conc. Ants', (0.5, 1.05), xycoords='axes fraction', ha='center')
        self.textbox_concurrent_ants = TextBox(plt.subplot(gs[2, 6]), '',
                                               initial=str(self.colony.waves[0].concurrent_ants))

        plt.subplot(gs[0:2, 6]).annotate('Ant Class', (0.5, 1.05), xycoords='axes fraction', ha='center')
        ax_radio = plt.subplot(gs[0:2, 6])
        ant_classes = ('random', 'routing', 'minority')
        initial_class_index = ant_classes.index(self.colony.waves[0].ant_class)
        self.radio_ant_class = RadioButtons(ax_radio, ('random', 'routing', 'minority'), active=initial_class_index)
        self.radio_ant_class.on_clicked(self.update_ant_class)

        self.start_colony_button = Button(plt.subplot(gs[3, 6]), label='Run Colony')
        self.start_colony_button.on_clicked(self.run_colony)

        self.stop_colony_button = Button(plt.subplot(gs[4, 6]), label='Stop Colony')
        self.stop_colony_button.on_clicked(self.stop_colony)
        self.stop_colony_button.ax.set_visible(False)

        self.save_graphml_button = Button(plt.subplot(gs[5, 6]), label='Save GraphML')
        self.save_graphml_button.on_clicked(self.save_graphml)

        # self.toggle_buttons_button = Button(plt.subplot(gs[4, 3]), label='Hide Buttons')
        # self.toggle_buttons_button.on_clicked(self.toggle_buttons)

        # -------------------------Seventh Row----------------------------#

        # Add a TextBox for displaying print messages (non-editable)
        plt.subplot(gs[6, 0:7]).annotate('Logs', (0.5, 1.05), xycoords='axes fraction', ha='center')
        ax_log = plt.subplot(gs[6, 0:7])
        self.textbox_logs = TextBox(ax_log, '', initial='')
        self.textbox_logs.set_active(False)

    def graph_visibly(self, label):
        """
        Changes visibility of the graph.

        :param label: str (unused)
        :return: None
        """
        self.show_graph = not self.show_graph
        if self.show_graph:
            self.ani.event_source.start()
        else:
            self.ani.event_source.stop()
        plt.draw()

    def update_spawn_node(self, text):
        """
        Update the spawn node for ants.

        :param text: The spawn node identifier. ex node AB
        :type text: str
        :return: None
        """
        self.colony.waves[0].ant_spawn_node = text

    def run_colony(self, label):
        """
        Updates all parameters and start the colony

        :param label: The label of Button (unused) but required
        :return: None
        """
        self.start_colony_button.ax.set_visible(False)
        self.stop_colony_button.ax.set_visible(True)
        self.update_parameters('')
        self.colony.start()

    def stop_colony(self, label):
        """
        Stops the colony

        :param label: The label of Button (unused) but required
        :return: None
        """
        self.stop_colony_button.ax.set_visible(False)
        self.start_colony_button.ax.set_visible(True)
        self.update_parameters('')
        self.colony.stop()

    def save_graphml(self, event):
        """
        Save the graph to a GraphML file, including all node and edge attributes.

        :param event: The event that triggered this save (unused) but required.
        :type event: object
        :return: None
        """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".graphml",
                                                 filetypes=[("GraphML files", "*.graphml"), ("All files", "*.*")])

        if file_path:
            # Add necessary attributes to nodes and edges
            for node in self.G.nodes:
                self.G.nodes[node]['label'] = str(node)
                self.G.nodes[node]['color'] = str(self.cmap_nodes(self.G.nodes[node]['value']))

            for u, v in self.G.edges:
                self.G.edges[u, v]['weight'] = float(self.G[u][v]['weight'])
                self.G.edges[u, v]['pheromone'] = float(self.G[u][v]['pheromone'])
                self.G.edges[u, v]['color'] = str(self.cmap_edges(self.G[u][v]['pheromone']))

            # Write the GraphML file
            nx.write_graphml(self.G, file_path)
            self.print_message(f"Graph saved to {file_path}")

    def print_message(self, msg):
        """
        Displays messages in UI

        :param msg: Display message
        :return: None
        """
        print(msg)
        self.textbox_logs.set_val(msg)

    def update_ant_class(self, label):
        """
        Update the ant class for the first wave of the colony.

        This method sets the ant class for ants in the first wave of the colony based on the selected radio button.
        Either random, routing or minority.

        :param label: The label of the selected radio button (unused) but required.
        :type label: str
        :return: None
        """
        self.colony.waves[0].ant_class = self.radio_ant_class.value_selected

    def update_parameters(self, event):
        """
        Update various parameters that have been set via the UI for all waves in the colony.

        :param event: The event that triggered this update (unused) but required.
        :type event: object
        :return: None
        :return:
        """

        try:
            alpha = float(self.textbox_alpha.text)
            beta = float(self.textbox_beta.text)
            random_chance = float(self.textbox_random_chance.text)
            ant_max_steps = int(self.textbox_ant_max_steps.text)
            max_iterations = int(self.textbox_max_iterations.text)
            concurrent_ants = int(self.textbox_concurrent_ants.text)
            evaporation_rate = float(self.textbox_evaporation_rate.text)

            for wave in self.colony.waves:
                wave.alpha = alpha
                wave.beta = beta
                wave.random_chance = random_chance
                wave.ant_max_steps = ant_max_steps
                wave.max_iterations = max_iterations
                wave.concurrent_ants = concurrent_ants
                wave.evaporation_rate = evaporation_rate

            self.print_message(f'Updated parameters: Alpha={alpha}, Beta={beta}, Random Chance={random_chance}, '
                               f'Max Steps={ant_max_steps}, Max Iterations={max_iterations},'
                               f' Concurrent Ants={concurrent_ants},'f'Evaporation Rate={evaporation_rate}')
        except ValueError:
            self.print_message("Please enter valid numerical values for all parameters.")

    def toggle_random_spawn(self, label):
        """
        Toggle the random spawn setting for ants.

        This method toggles the random spawn setting for ants in the first wave of the colony.
        It also enables or disables the spawn node text box based on the new state.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """

        self.colony.waves[0].ant_random_spawn = not self.colony.waves[0].ant_random_spawn
        if self.colony.waves[0].ant_random_spawn:
            self.textbox_spawn_node.set_active(False)
            self.textbox_spawn_node.ax.set_visible(False)
        else:
            self.textbox_spawn_node.set_active(True)
            self.textbox_spawn_node.ax.set_visible(True)

    def toggle_put_pheromones_always(self, label):
        """
        Toggle the put pheromones always setting.

        This method toggles whether ants always put down pheromones in the first wave of the colony.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """
        self.colony.waves[0].put_pheromones_always = not self.colony.waves[0].put_pheromones_always

    def toggle_stop_on_success(self, label):
        """
        Toggle the stop on success setting.

        This method toggles whether the ants of the colony die when they reach a success node
        (multiple success nodes are possible) or continue to live.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """
        self.colony.waves[0].stop_on_success = not self.colony.waves[0].stop_on_success

    def toggle_prioritize_pheromone_routes(self, label):
        """
        Toggle the priority pheromone routes setting.

        This method toggles whether MINORITY ants only prioritize routes with the least pheromones or all routes.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """
        self.colony.waves[0].prioritize_pheromone_routes = not self.colony.waves[0].prioritize_pheromone_routes

    def update_step_sleep(self, text):
        """
        Update the step sleep time for all waves in the colony.

        This method updates the duration between ant steps.

        :param text: The new step sleep time.
        :type text: str
        :return: None
        """
        try:
            val = float(text)
            self.print_message(f'Step sleep set to {val}')
            for wave in self.colony.waves:
                wave.step_sleep = val
        except ValueError:
            self.print_message("Please enter a valid number for step sleep.")

    def update_iteration_sleep(self, text):
        """
        Update the step sleep time for all waves in the colony.

        This method updates the duration between iterations.
        Iterations contain all the ants.

        :param text: The new step sleep time.
        :type text: str
        :return: None
        """
        try:
            val = float(text)
            self.print_message(f'Iteration sleep set to {val}')
            for wave in self.colony.waves:
                wave.iteration_sleep = val
        except ValueError:
            self.print_message("Please enter a valid number for iteration sleep.")

    def update_wave_sleep(self, text):
        """
        Update the step sleep time for all waves in the colony.

        This method updates the duration between waves.
        Waves contain all the iterations.

        :param text: The new step sleep time.
        :type text: str
        :return: None
        """
        try:
            val = float(text)
            self.print_message(f'Wave sleep set to {val}')
            for wave in self.colony.waves:
                wave.wave_sleep = val
        except ValueError:
            self.print_message("Please enter a valid number for wave sleep.")

    def toggle_buttons(self, event):
        """
        Toggle the visibility of control buttons and text boxes.

        This method toggles the visibility of various control buttons and text boxes in the
        user interface.

        :param event: The event that triggered this toggle (unused) but required.
        :type event: object
        :return: None
        """

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
        """
        Reset the colony and reinitialize the configuration.

        This method stops the current colony activity, closes the existing plot,
        reinitialized the configuration from the given path, and sets up the plot again.

        :param config_path: The path to the configuration file.
        :type config_path: str
        :return: None
        """
        self.colony.stop()
        plt.close(self.fig)
        self.init_config(config_path)
        self.setup_plot()

    def save_config(self, event):
        """
        Save the current configuration to a JSON file.

        This method updates the parameters, opens a file dialog for the user to specify the
        save location, and saves the current configuration to a JSON file.

        :param event: The event that triggered this save (unused) but required.
        :type event: object
        :return: None
        """
        self.update_parameters('')
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])

        if file_path:
            with open(file_path, 'w') as f:
                json.dump(GraphTools.save_config_as_json(self), f, indent=4)
            self.print_message(f"Configuration saved to {file_path}")

    def on_load_config_clicked(self, event):
        """
        Load a configuration from a JSON file and reset the colony.

        This method opens a file dialog for the user to select a configuration file,
        and resets the colony with the selected configuration.

        :param event: The event that triggered this load (unused) but required.
        :type event: object
        :return: None
        """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.reset(file_path)

    def update_check_edge(self, label):
        """
        Toggle the visibility of edge parameters.

        This method toggles the visibility of edge parameters in the plot.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """
        self.show_edge_parameters = not self.show_edge_parameters

    def update_check_ant(self, label):
        """
        Toggle the visibility of ant animation.

        This method toggles the visibility of the ant animation in the plot.

        :param label: The label associated with the toggle (unused) but required.
        :type label: str
        :return: None
        """
        self.show_ant_animation = not self.show_ant_animation

    def update_plot(self, frame):
        """
        renders the graph
        """

        # Find the minimum and maximum weight among all edges in the graph
        min_weight, max_weight = min(data['weight'] for _, _, data in self.G.edges(data=True)), max(
            data['weight'] for _, _, data in self.G.edges(data=True))

        # Find the minimum and maximum pheromone level among all edges in the graph
        min_pheromone, max_pheromone = min(data['pheromone'] for _, _, data in self.G.edges(data=True)), max(
            data['pheromone'] for _, _, data in self.G.edges(data=True))

        # Find the minimum and maximum value among all nodes in the graph
        min_value, max_value = min(data['value'] for _, data in self.G.nodes(data=True)), max(
            data['value'] for _, data in self.G.nodes(data=True))

        # Normalize the node values and edge pheromone levels for color mapping
        node_norm = mcolors.Normalize(vmin=min_value, vmax=max_value)
        edge_norm = mcolors.Normalize(vmin=min_pheromone, vmax=max_pheromone)

        self.ax.clear()

        # Generate the color map for nodes based on their values
        node_colors = [self.cmap_nodes(node_norm(data['value'])) for _, data in self.G.nodes(data=True)]
        nodes = nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=list(self.G.nodes()), node_color=node_colors,
                                       ax=self.ax)

        edges = self.G.edges(data=True)

        # Generate the color map for edges based on their pheromone levels
        edge_colors = [self.cmap_edges(edge_norm(data['pheromone'])) for _, _, data in edges]
        # Calculate the width for each edge based on its weight
        widths = [1 + (data['weight'] - min_weight) / (max_weight - min_weight + 1) for _, _, data in edges]
        edges = nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=list(edges), width=widths,
                                       edge_color=edge_colors,
                                       connectionstyle="arc3,rad=0.07", ax=self.ax)

        node_labels = nx.draw_networkx_labels(self.G, self.pos, font_size=self.node_label_size, ax=self.ax,
                                              font_color=self.node_label_color,
                                              labels={n: n for n in self.G.nodes()})

        # If edge parameters are to be shown, draw edge weight and pheromone labels
        if self.show_edge_parameters:
            # Create labels for edge weights
            weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
            edge_weight_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels,
                                                              font_color=self.edge_weight_label_color,
                                                              label_pos=0.1, ax=self.ax)

            # Create labels for edge pheromone levels
            pheromone_labels = {(tail, head): f"{round(data['pheromone'], 1)}" for tail, head, data in
                                self.G.edges(data=True)}
            edge_pheromone_labels = nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels,
                                                                 font_color=self.edge_pheromone_label_color,
                                                                 label_pos=0.3, ax=self.ax)

            # Collect all artists (visual elements) to be drawn required for animations
            artists = [nodes] + list(edges) + list(node_labels.values()) + list(edge_weight_labels.values()) + list(
                edge_pheromone_labels.values())
        else:
            # Collect only the node and edge artists if edge parameters are not shown
            artists = [nodes] + list(edges) + list(node_labels.values())

        # If there are ants and ant animation is enabled, draw the ants on the graph
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
            #if not self.colony.waves[0].ant_random_spawn:
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
