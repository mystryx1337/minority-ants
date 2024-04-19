from typing import List

import networkx as nx
import matplotlib.pyplot as plt
import threading
from matplotlib.widgets import Button

G = nx.DiGraph()

# Kanten mit Gewichten und Pheromonen hinzufügen
G.add_edges_from([("A", "B", {'weight': 2, 'pheromone': 0.5}),
                  ("B", "A", {'weight': 2, 'pheromone': 0.7}),
                  ("B", "C", {'weight': 4, 'pheromone': 0.3}),
                  ("C", "D", {'weight': 1, 'pheromone': 0.8}),
                  ("D", "E", {'weight': 3, 'pheromone': 0.2}),
                  ("E", "B", {'weight': 5, 'pheromone': 0.6})])


class Button_Callback:
    def add_edge(self):
        global G, pos

        tail = input("Geben Sie den Startknoten der neuen Kante ein: ")
        head = input("Geben Sie den Zielknoten der neuen Kante ein: ")
        weight = float(input("Geben Sie das Gewicht der neuen Kante ein: "))


        #Graphen redesignen, wenn neuer Knoten erzeugt wird
        if not G.has_node(tail) or not G.has_node(head):
            G.add_edge(tail, head, weight=weight, pheromone=0.0)
            pos = nx.spring_layout(G)
        else:
            G.add_edge(tail, head, weight=weight, pheromone=0.0)

        update_plot()

    def delete_edge(self):
        global G

        tail = input("Geben Sie den Startknoten der Kante ein: ")
        head = input("Geben Sie den Zielknoten der Kante ein: ")

        # Hinzufügen der Kante zum Graphen
        G.remove_edge(tail, head)

        #TODO: Knoten löschen, wenn keine Kante mehr exisitiert
        #und dann Redesign

        update_plot()

def update_plot():
    global G, pos, weight_labels, pheromone_labels, node_colors, fig

    # Zeichne den Graphen mit den aktualisierten Kanten
    plt.cla()  # Lösche vorherige Zeichnung

    weight_labels = {(tail, head): f"{data['weight']}" for tail, head, data in G.edges(data=True)}
    pheromone_labels = {(tail, head): f"{data['pheromone']}" for tail, head, data in G.edges(data=True)}
    node_colors = ["purple"] * len(G.nodes)
    edge_colors = ["black"] * len(G.edges)

    nx.draw(G, pos, node_color=node_colors, with_labels=False)
    nx.draw_networkx_labels(G, pos, font_size=12, font_color="white", labels={n: n for n in G.nodes()})
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels, font_color='red', label_pos=0.1)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pheromone_labels, font_color='blue', label_pos=0.3)

    #fig.canvas.draw()
    plt.draw()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pos = nx.spring_layout(G)  # positions for all nodes
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)  # Ändere den unteren Rand des Plots, um Platz für den Knopf zu schaffen

    add_edge_ax = fig.add_axes([0.02, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
    add_edge_button = Button(add_edge_ax, label='Neue Kante')  # Erstelle den Knopf
    add_edge_button.on_clicked(Button_Callback.add_edge)  # Füge den Callback hinzu

    delete_edge_ax = fig.add_axes([0.22, 0.02, 0.18, 0.06])  # Position und Größe des Knopfes
    delete_edge_button = Button(delete_edge_ax, label='Kante löschen')  # Erstelle den Knopf
    delete_edge_button.on_clicked(Button_Callback.delete_edge)  # Füge den Callback hinzu

    plt.sca(ax)
    update_plot()

    plt.show()
