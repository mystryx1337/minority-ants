import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as mpl
import networkx as nx
from matplotlib.widgets import Button, TextBox
import colony


class Edge:
    def __init__(self, tail, head, weight):
        self.tail = tail
        self.head = head
        self.weight = weight


class AcoPlot:
    G: nx.DiGraph
    pos: dict

    def __init__(self, G):
        self.G = G
        self.colony = colony.AntColonyRunner(G, self)

        # colormaps  https://matplotlib.org/stable/users/explain/colors/colormaps.html
        self.cmap_cool = mpl.colormaps['cool']
        self.cmap_winter = mpl.colormaps['winter']

        #area for buttons
        self.pos = nx.spring_layout(self.G)  # positions for all nodes
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

        #buttons and input-fields
        add_edge_ax = self.fig.add_axes([0.1, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        add_edge_button = Button(add_edge_ax, label='Add')
        add_edge_button.on_clicked(lambda event: self.add_edge(textbox_tail.text, textbox_head.text,
                                                                    textbox_weight.text))  # Füge den Callback hinzu

        ax_tail = self.fig.add_axes([0.25, 0.05, 0.05, 0.075])
        textbox_tail = TextBox(ax_tail, 'Start ')

        ax_head = self.fig.add_axes([0.35, 0.05, 0.05, 0.075])
        textbox_head = TextBox(ax_head, 'Ende ')

        ax_weight = self.fig.add_axes([0.45, 0.05, 0.05, 0.075])
        textbox_weight = TextBox(ax_weight, 'Weight ')

        delete_edge_ax = self.fig.add_axes([0.55, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        delete_edge_button = Button(delete_edge_ax, label='Remove')
        delete_edge_button.on_clicked(
            lambda event: self.delete_edge(textbox_tail.text, textbox_head.text))  # Füge den Callback hinzu

        start_colony_ax = self.fig.add_axes([0.75, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        start_colony_button = Button(start_colony_ax, label='Run Colony')
        start_colony_button.on_clicked(
            lambda event: self.colony.start())  # Füge den Callback hinzu

        #set focus to plot area
        plt.sca(self.ax)

        #draw initial graph
        self.update_plot()

        #keep the graph-window
        plt.show()
        self.colony.stop()

    def update_plot(self):
        # draw graph with current edges
        try:
            min_weight = min([data['weight'] for (u, v, data) in self.G.edges(data=True)])
            max_weight = max([data['weight'] for (u, v, data) in self.G.edges(data=True)])

            min_pheromone = min([data['pheromone'] for (u, v, data) in self.G.edges(data=True)])
            max_pheromone = max([data['pheromone'] for (u, v, data) in self.G.edges(data=True)])

            min_value = min([data['value'] for (u, data) in self.G.nodes(data=True)])
            max_value = max([data['value'] for (u, data) in self.G.nodes(data=True)])

            # Definiere die Farbskala für die Pheromonausprägung
            edge_norm = mcolors.Normalize(vmin=min_pheromone, vmax=max_pheromone)

            # Definiere die Farbskala für die Pheromonausprägung
            node_norm = mcolors.Normalize(vmin=min_value, vmax=max_value)

            plt.cla()  # delete previous plotted draw

            # Zeichne die Knoten
            for (u, data) in self.G.nodes(data=True):
                node_color = self.cmap_winter(node_norm(data['value']))
                nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=[u], node_color=node_color)

            # Zeichne die Kanten
            for (u, v, data) in self.G.edges(data=True):
                # Berechne die Kantendicke basierend auf dem Gewicht
                edge_color = self.cmap_cool(edge_norm(data['pheromone']))
                width = 1 + (data['weight'] - min_weight) / (max_weight - min_weight)
                nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=[(u, v)], width=width, edge_color=edge_color, connectionstyle="arc3,rad=0.07")


            weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
            pheromone_labels = {(tail, head): f"{data['pheromone']}" for tail, head, data in self.G.edges(data=True)}

            nx.draw_networkx_labels(self.G, self.pos, font_size=12, font_color="white",
                                    labels={n: n for n in self.G.nodes()})
            nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels, font_color='red', label_pos=0.1)
            nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels, font_color='blue', label_pos=0.3)

            self.fig.canvas.draw()

        except: #window is already closed and thread tries to update plot
            pass

    def add_edge(self, tail, head, weight):
        global G, pos

        try:
            weight = float(weight)
        except ValueError:
            weight = 1.0

        if not self.G.has_node(tail) or not self.G.has_node(head):
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
            self.pos = nx.spring_layout(self.G)  # Recalculate layout
        else:
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
        self.update_plot()

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

        self.update_plot()
