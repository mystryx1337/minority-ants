from tkinter import *
import tkinter as tk

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.widgets import Button


class Edge:
    def __init__(self, tail, head, weight):
        self.tail = tail
        self.head = head
        self.weight = weight


class Render:
    def __init__(self, G):
        self.G = G

        self.pos = nx.spring_layout(G)  # positions for all nodes
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

        add_edge_ax = fig.add_axes([0.02, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
        self.add_edge_button = Button(add_edge_ax, label='Neue Kante')
        self.add_edge_button.on_clicked(self.input_field)  # Füge den Callback hinzu

        delete_edge_ax = fig.add_axes([0.22, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
        self.delete_edge_button = Button(delete_edge_ax, label='Kante löschen')
        self.delete_edge_button.on_clicked(self.input_field_delete)  # Füge den Callback hinzu

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

        if not self.G.has_node(tail) or not self.G.has_node(head):
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
            self.pos = nx.spring_layout(self.G)  # Recalculate layout
        else:
            self.G.add_edge(tail, head, weight=weight, pheromone=0.0)
        self.update_plot()

    def input_field(self, event):
        self.input_root = tk.Tk()
        self.input_root.title("Add Edge")
        Label(self.input_root, text="Startknoten").grid(row=0)
        Label(self.input_root, text="Zielknoten").grid(row=1)
        Label(self.input_root, text="Gewicht").grid(row=2)

        # Entries
        tail_entry = Entry(self.input_root)
        tail_entry.grid(row=0, column=1)
        head_entry = Entry(self.input_root)
        head_entry.grid(row=1, column=1)
        weight_entry = Entry(self.input_root)
        weight_entry.grid(row=2, column=1)

        # Submit button
        submit_btn = tk.Button(self.input_root, text="Submit",
                               command=lambda: self.submit_edge(tail_entry, head_entry, weight_entry))
        submit_btn.grid(row=3, columnspan=2)

        self.input_root.mainloop()

    def submit_edge(self, tail_entry, head_entry, weight_entry):
        tail = tail_entry.get()
        head = head_entry.get()
        weight = float(weight_entry.get())
        self.add_edge(tail, head, weight)
        self.input_root.destroy()  # Close the input window

    def input_field_delete(self, event):
        self.delete_root = tk.Tk()
        self.delete_root.title("Delete Edge")
        Label(self.delete_root, text="Startknoten").grid(row=0)
        Label(self.delete_root, text="Zielknoten").grid(row=1)

        # Entries
        tail_entry = Entry(self.delete_root)
        tail_entry.grid(row=0, column=1)
        head_entry = Entry(self.delete_root)
        head_entry.grid(row=1, column=1)

        # Delete button
        delete_btn = tk.Button(self.delete_root, text="Delete",
                               command=lambda: self.delete_edge(tail_entry, head_entry))
        delete_btn.grid(row=2, columnspan=2)

        self.delete_root.mainloop()

    def delete_edge(self, tail_entry, head_entry):
        tail = tail_entry.get()
        head = head_entry.get()

        # Entfernen der Kante zum Graphen
        self.G.remove_edge(tail, head)

        # TODO: Knoten löschen, wenn keine Kante mehr exisitiert
        # und dann Redesign

        self.update_plot()

    def input_field_delete(self, event):
        self.delete_root = tk.Tk()
        self.delete_root.title("Delete Edge")
        Label(self.delete_root, text="Startknoten").grid(row=0)
        Label(self.delete_root, text="Zielknoten").grid(row=1)

        # Entries
        tail_entry = Entry(self.delete_root)
        tail_entry.grid(row=0, column=1)
        head_entry = Entry(self.delete_root)
        head_entry.grid(row=1, column=1)

        # Delete button
        delete_btn = tk.Button(self.delete_root, text="Delete",
                               command=lambda: self.delete_edge(tail_entry, head_entry))
        delete_btn.grid(row=2, columnspan=2)

        self.delete_root.mainloop()
