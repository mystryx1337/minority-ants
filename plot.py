import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class Render:
    def __init__(self, G):
        self.G = G

        self.pos = nx.spring_layout(G)  # positions for all nodes
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

        add_edge_ax = fig.add_axes([0.02, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
        add_edge_button = Button(add_edge_ax, label='Neue Kante')  # Erstelle den Knopf
        add_edge_button.on_clicked(self.add_edge)  # Füge den Callback hinzu

        delete_edge_ax = fig.add_axes([0.22, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
        delete_edge_button = Button(delete_edge_ax, label='Kante löschen')  # Erstelle den Knopf
        delete_edge_button.on_clicked(self.delete_edge)  # Füge den Callback hinzu

        plt.sca(ax)
        self.update_plot()

        plt.show()

    def update_plot(self):

        # Zeichne den Graphen mit den aktualisierten Kanten
        plt.cla()  # Lösche vorherige Zeichnung

        weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
        pheromone_labels = {(tail, head): f"{data['pheromone']}" for tail, head, data in self.G.edges(data=True)}
        node_colors = ["purple"] * len(self.G.nodes)
        #edge_colors = ["black"] * len(self.G.edges)

        nx.draw(self.G, self.pos, node_color=node_colors, with_labels=False)
        nx.draw_networkx_labels(self.G, self.pos, font_size=12, font_color="white", labels={n: n for n in self.G.nodes()})
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels, font_color='red', label_pos=0.1)
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels, font_color='blue', label_pos=0.3)

        # fig.canvas.draw()
        plt.draw()

    def add_edge(self, event):
        global G, pos

        tail = input("Geben Sie den Startknoten der neuen Kante ein: ")
        head = input("Geben Sie den Zielknoten der neuen Kante ein: ")
        weight = float(input("Geben Sie das Gewicht der neuen Kante ein: "))

        # Graphen redesignen, wenn neuer Knoten erzeugt wird
        if not self.G.has_node(tail) or not self.G.has_node(head):
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
            self.pos = nx.spring_layout(self.G)
        else:
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)

        self.update_plot()

    def delete_edge(self, event):
        tail = input("Geben Sie den Startknoten der Kante ein: ")
        head = input("Geben Sie den Zielknoten der Kante ein: ")

        # Hinzufügen der Kante zum Graphen
        self.G.remove_edge(tail, head)

        # TODO: Knoten löschen, wenn keine Kante mehr exisitiert
        # und dann Redesign

        self.update_plot()