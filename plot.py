from tkinter import *
import tkinter as tk

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.widgets import Button, TextBox


class Edge:
    def __init__(self, tail, head, weight):
        self.tail = tail
        self.head = head
        self.weight = weight


class Render:
    def __init__(self, G):
        self.G = G

        self.pos = nx.spring_layout(G)  # positions for all nodes
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

        ax_tail = fig.add_axes([0.25, 0.05, 0.1, 0.075])
        textbox_tail = TextBox(ax_tail, 'Start')

        ax_head = fig.add_axes([0.4, 0.05, 0.1, 0.075])
        textbox_head = TextBox(ax_head, 'Ende')

        ax_weight = fig.add_axes([0.55, 0.05, 0.1, 0.075])
        textbox_weight = TextBox(ax_weight, 'Weight')

        add_edge_ax = fig.add_axes([0.1, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        self.add_edge_button = Button(add_edge_ax, label='Add')
        self.add_edge_button.on_clicked(lambda event: self.add_edge(textbox_tail.text, textbox_head.text, textbox_weight.text))  # Füge den Callback hinzu

        delete_edge_ax = fig.add_axes([0.7, 0.05, 0.1, 0.075])  # Position und Größe des Knopfes
        self.delete_edge_button = Button(delete_edge_ax, label='Remove')
        self.delete_edge_button.on_clicked(lambda event: self.delete_edge(textbox_tail.text, textbox_head.text))  # Füge den Callback hinzu

        plt.sca(ax)
        self.update_plot()

        plt.show()

    def update_plot(self):

        # Zeichne den Graphen mit den aktualisierten Kanten
        plt.cla()  # Lösche vorherige Zeichnung

        weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in self.G.edges(data=True)}
        pheromone_labels = {(tail, head): f"{data['pheromone']}" for tail, head, data in self.G.edges(data=True)}
        node_colors = ["purple"] * len(self.G.nodes)
        # edge_colors = ["black"] * len(self.G.edges)

        nx.draw(self.G, self.pos, node_color=node_colors, with_labels=False)
        nx.draw_networkx_labels(self.G, self.pos, font_size=12, font_color="white",
                                labels={n: n for n in self.G.nodes()})
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=weight_labels, font_color='red', label_pos=0.1)
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=pheromone_labels, font_color='blue', label_pos=0.3)

        # fig.canvas.draw()
        plt.draw()

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
        except nx.NetworkXError:  # Kante existiert nicht
            pass

        # TODO: Knoten löschen, wenn keine Kante mehr exisitiert
        # und dann Redesign

        self.update_plot()